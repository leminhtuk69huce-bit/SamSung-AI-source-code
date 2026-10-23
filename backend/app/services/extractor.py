import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

VIETNAMESE_UPPERCASE_REGEX = re.compile(r"^[A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ\s]+$")
DATE_REGEX = re.compile(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b")
ID_NUMBER_REGEX_12 = re.compile(r"\b\d{12}\b")
ID_NUMBER_REGEX_9 = re.compile(r"\b\d{9}\b")

# Ignored texts that look like names or headers
IGNORE_HEADERS = [
    "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
    "CỘNG HÒA XÃ HỘI",
    "CỘNG HÒA",
    "ĐỘC LẬP TỰ DO HẠNH PHÚC",
    "ĐỘC LẬP - TỰ DO - HẠNH PHÚC",
    "ĐỘC LẬP", "TỰ DO", "HẠNH PHÚC",
    "CĂN CƯỚC CÔNG DÂN",
    "CHỨNG MINH NHÂN DÂN",
    "SOCIALIST REPUBLIC OF VIET NAM",
    "CITIZEN IDENTITY CARD",
    "INDEPENDENCE", "FREEDOM", "HAPPINESS"
]

def clean_vietnamese_text(text: str) -> str:
    """Removes stray leading/trailing colons, dots, dashes, and extra spaces."""
    t = text.strip()
    t = re.sub(r"^[\s:;.,\-_]+", "", t)
    t = re.sub(r"[\s:;.,\-_]+$", "", t)
    return t.strip()

def classify_side(raw_boxes: List[Dict[str, Any]]) -> str:
    """Determines whether the scanned card is FRONT side or BACK side."""
    full_text = " ".join([b["text"].lower() for b in raw_boxes])
    
    front_score = 0
    back_score = 0

    front_keywords = ["căn cước", "chứng minh", "số /", "no:", "họ và tên", "ngày sinh", "giới tính", "quê quán", "thường trú", "có giá trị đến", "nationality", "sex"]
    back_keywords = ["đặc điểm", "nhân dạng", "ngón trỏ", "cục trưởng", "quản lý hành chính", "ngày, tháng", "date; month", "công an", "mrz", "trái", "phải"]

    for kw in front_keywords:
        if kw in full_text:
            front_score += 1
            
    for kw in back_keywords:
        if kw in full_text:
            back_score += 1

    if back_score > front_score and back_score >= 2:
        return "BACK"
    return "FRONT"

def classify_document_type(raw_boxes: List[Dict[str, Any]]) -> str:
    """Classifies document: CCCD_CHIP, CCCD_BARCODE, CMND_12, CMND_9."""
    full_text = " ".join([b["text"].upper() for b in raw_boxes])

    if "CĂN CƯỚC" in full_text or "CITIZEN" in full_text:
        return "CCCD_CHIP"
    elif "CHỨNG MINH" in full_text:
        # Check digit count
        digits = re.findall(r"\b\d{9,12}\b", full_text)
        if any(len(d) == 12 for d in digits):
            return "CMND_12"
        return "CMND_9"
    return "CCCD_CHIP"

def extract_fields(raw_boxes: List[Dict[str, Any]], side_hint: Optional[str] = "auto") -> Dict[str, Any]:
    """
    Main extraction pipeline.
    Takes sorted OCR bounding boxes and extracts key fields with confidences.
    """
    side = side_hint if side_hint in ["FRONT", "BACK"] else classify_side(raw_boxes)
    doc_type = classify_document_type(raw_boxes)

    fields: Dict[str, Dict[str, Any]] = {
        "id_number": {"value": None, "confidence": 0.0},
        "full_name": {"value": None, "confidence": 0.0},
        "date_of_birth": {"value": None, "confidence": 0.0},
        "gender": {"value": None, "confidence": 0.0},
        "nationality": {"value": None, "confidence": 0.0},
        "place_of_origin": {"value": None, "confidence": 0.0},
        "place_of_residence": {"value": None, "confidence": 0.0},
        "date_of_expiry": {"value": None, "confidence": 0.0},
        "date_of_issue": {"value": None, "confidence": 0.0},
        "issuing_authority": {"value": None, "confidence": 0.0},
        "identifying_features": {"value": None, "confidence": 0.0},
        "mrz_code": {"value": None, "confidence": 0.0},
    }

    n = len(raw_boxes)

    if side == "FRONT":
        fields["nationality"] = {"value": "Việt Nam", "confidence": 0.99}

        # 1. ID Number
        for i, box in enumerate(raw_boxes):
            t = box["text"]
            # Look for 12 or 9 consecutive digits
            m12 = ID_NUMBER_REGEX_12.search(t)
            if m12:
                fields["id_number"] = {"value": m12.group(0), "confidence": box["confidence"]}
                break
            m9 = ID_NUMBER_REGEX_9.search(t)
            if m9 and not fields["id_number"]["value"]:
                fields["id_number"] = {"value": m9.group(0), "confidence": box["confidence"]}

            # If line is "Số / No:" check next line
            if re.search(r"\b(số|no|so)\b", t, re.IGNORECASE) and i + 1 < n:
                next_t = raw_boxes[i+1]["text"]
                m = re.search(r"\b\d{9,12}\b", next_t)
                if m:
                    fields["id_number"] = {"value": m.group(0), "confidence": raw_boxes[i+1]["confidence"]}

        # 2. Full Name
        for i, box in enumerate(raw_boxes):
            t = box["text"].strip()
            # If line contains label "Họ và tên" / "Full name"
            if re.search(r"họ\s*(và|v)\s*tên|full\s*name", t, re.IGNORECASE):
                # Check if name is attached on the same line after colon
                colon_split = re.split(r"[:;]", t, maxsplit=1)
                if len(colon_split) > 1 and len(colon_split[1].strip()) >= 3:
                    cand = clean_vietnamese_text(colon_split[1])
                    if VIETNAMESE_UPPERCASE_REGEX.match(cand):
                        fields["full_name"] = {"value": cand, "confidence": box["confidence"]}
                        break
                # Or it's on the next line
                if i + 1 < n:
                    next_cand = clean_vietnamese_text(raw_boxes[i+1]["text"])
                    # Check if all caps and not header
                    if len(next_cand) >= 3 and VIETNAMESE_UPPERCASE_REGEX.match(next_cand):
                        if not any(h in next_cand.upper() for h in IGNORE_HEADERS):
                            fields["full_name"] = {"value": next_cand, "confidence": raw_boxes[i+1]["confidence"]}
                            break

        # Fallback for Full Name: scan for any standalone all-caps Vietnamese name line
        if not fields["full_name"]["value"]:
            for box in raw_boxes:
                cand = clean_vietnamese_text(box["text"])
                if len(cand) >= 4 and len(cand) <= 35 and VIETNAMESE_UPPERCASE_REGEX.match(cand):
                    if not any(h in cand.upper() for h in IGNORE_HEADERS) and "NGÀY" not in cand and "SỐ" not in cand:
                        fields["full_name"] = {"value": cand, "confidence": box["confidence"]}
                        break

        # 3. Collect all dates on front side for intelligent classification
        all_dates = []
        for i, box in enumerate(raw_boxes):
            for m in DATE_REGEX.finditer(box["text"]):
                d, mth, y = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
                all_dates.append({
                    "date": f"{d}/{mth}/{y}",
                    "day": int(d),
                    "month": int(mth),
                    "year": int(y),
                    "conf": box["confidence"],
                    "box_idx": i,
                    "text": box["text"]
                })

        # Check for expiry "Không thời hạn"
        for box in raw_boxes:
            if re.search(r"không\s*thời\s*hạn", box["text"], re.IGNORECASE):
                fields["date_of_expiry"] = {"value": "Không thời hạn", "confidence": box["confidence"]}
                break

        # Associate dates with birth or expiry based on local context
        dob_cand = None
        exp_cand = None

        for item in all_dates:
            ctx = item["text"]
            if item["box_idx"] > 0:
                ctx += " " + raw_boxes[item["box_idx"] - 1]["text"]
            if item["box_idx"] + 1 < n:
                ctx += " " + raw_boxes[item["box_idx"] + 1]["text"]

            if re.search(r"sinh|birth", ctx, re.IGNORECASE) and not dob_cand:
                dob_cand = item
            elif re.search(r"giá\s*t[r|i|í]\s*đến|cógiá|tíđến|expiry|hết\s*hạn", ctx, re.IGNORECASE) and not exp_cand:
                exp_cand = item

        # Smart fallback: if either is missing, use year heuristics
        # (Birth year is <= 2024, Expiry year is >= 2025)
        if all_dates:
            sorted_dates = sorted(all_dates, key=lambda x: x["year"])
            if not dob_cand:
                past_dates = [d for d in sorted_dates if d["year"] <= 2024]
                if past_dates:
                    dob_cand = past_dates[0]
            if not exp_cand and not fields["date_of_expiry"]["value"]:
                future_dates = [d for d in sorted_dates if d["year"] >= 2025]
                if future_dates:
                    exp_cand = future_dates[-1]
                elif len(sorted_dates) >= 2 and sorted_dates[-1] != dob_cand:
                    exp_cand = sorted_dates[-1]

        if dob_cand:
            fields["date_of_birth"] = {"value": dob_cand["date"], "confidence": dob_cand["conf"]}
        if exp_cand and not fields["date_of_expiry"]["value"]:
            fields["date_of_expiry"] = {"value": exp_cand["date"], "confidence": exp_cand["conf"]}

        # 4. Gender
        for i, box in enumerate(raw_boxes):
            t = box["text"]
            if re.search(r"giới\s*tính|sex", t, re.IGNORECASE):
                if re.search(r"\bnam\b", t, re.IGNORECASE):
                    fields["gender"] = {"value": "Nam", "confidence": box["confidence"]}
                    break
                elif re.search(r"\bnữ\b|\bnu\b", t, re.IGNORECASE):
                    fields["gender"] = {"value": "Nữ", "confidence": box["confidence"]}
                    break
                # Look at next boxes if label is separated
                for offset in [1, 2]:
                    if i + offset < n:
                        next_t = raw_boxes[i + offset]["text"]
                        if re.search(r"^nam\b|\bnam\s*quốc\s*tịch", next_t, re.IGNORECASE) or next_t.strip().lower() == "nam":
                            fields["gender"] = {"value": "Nam", "confidence": raw_boxes[i + offset]["confidence"]}
                            break
                        elif re.search(r"^nữ\b|\bnu\b|\bnữ\s*quốc\s*tịch", next_t, re.IGNORECASE) or next_t.strip().lower() in ["nữ", "nu"]:
                            fields["gender"] = {"value": "Nữ", "confidence": raw_boxes[i + offset]["confidence"]}
                            break
                if fields["gender"]["value"]:
                    break
            elif t.strip() in ["Nam", "Nữ", "NAM", "NỮ"]:
                fields["gender"] = {"value": "Nam" if "nam" in t.lower() else "Nữ", "confidence": box["confidence"]}
                break

        # Fallback for Gender: decode from 4th digit of 12-digit CCCD
        if not fields["gender"]["value"] and fields["id_number"]["value"] and len(fields["id_number"]["value"]) == 12:
            try:
                gender_digit = int(fields["id_number"]["value"][3])
                fields["gender"] = {
                    "value": "Nam" if gender_digit % 2 == 0 else "Nữ",
                    "confidence": 0.95
                }
            except Exception:
                pass

        # Helper to clean address strings
        def clean_address(raw_str: str) -> str:
            t = raw_str
            # Extract and save expiry date if hidden in address
            date_m = DATE_REGEX.search(t)
            if date_m and not fields["date_of_expiry"]["value"]:
                d_val = f"{date_m.group(1).zfill(2)}/{date_m.group(2).zfill(2)}/{date_m.group(3)}"
                if int(date_m.group(3)) >= 2025:
                    fields["date_of_expiry"] = {"value": d_val, "confidence": 0.9}
            # Remove dates
            t = DATE_REGEX.sub("", t)
            # Remove expiry label bleed
            t = re.sub(r"(có\s*giá\s*t[r|i|í]\s*đến|cógiá\s*tíđến|cógiá|tíđến|có\s*giá\s*trị|hết\s*hạn|date\s*of\s*expiry|'ofexpiry|ofexpiry|expiry)[:;]?", "", t, flags=re.IGNORECASE)
            t = re.sub(r"['‘’\"]", "", t)
            t = re.sub(r"\b(date|expiry|ofexpiry|hết\s*hạn)\b", "", t, flags=re.IGNORECASE)
            t = re.sub(r"\s*,\s*", ", ", t)
            t = re.sub(r",(\s*,)+", ",", t)
            # Fix split syllables like "Đại, áng" -> "Đại Áng"
            def fix_split_syllable(m):
                return m.group(1) + " " + m.group(2).capitalize()
            t = re.sub(r"\b([A-ZÀ-Ỹa-zà-ỹ]+),\s*([a-zà-ỹ]+)\b", fix_split_syllable, t)
            t = re.sub(r"\s*,\s*", ", ", t)
            t = re.sub(r"^[\s,;:.-]+", "", t)
            t = re.sub(r"[\s,;:.-]+$", "", t)
            return clean_vietnamese_text(t)

        # 5. Place of Origin (Quê quán)
        origin_parts = []
        origin_confs = []
        recording_origin = False
        for box in raw_boxes:
            t = box["text"]
            if re.search(r"quê\s*quán|place\s*of\s*origin", t, re.IGNORECASE):
                recording_origin = True
                cleaned = re.sub(r".*?(quê\s*quán|origin)[:;]?", "", t, flags=re.IGNORECASE).strip()
                if cleaned:
                    origin_parts.append(cleaned)
                    origin_confs.append(box["confidence"])
                continue

            if recording_origin:
                if re.search(r"thường\s*trú|residence|nơi", t, re.IGNORECASE):
                    recording_origin = False
                    break
                origin_parts.append(t.strip())
                origin_confs.append(box["confidence"])

        if origin_parts:
            raw_orig = ", ".join(origin_parts).replace(";,", ",")
            fields["place_of_origin"] = {
                "value": clean_address(raw_orig),
                "confidence": round(sum(origin_confs) / len(origin_confs), 2)
            }

        # 6. Place of Residence (Nơi thường trú)
        residence_parts = []
        residence_confs = []
        recording_residence = False
        for box in raw_boxes:
            t = box["text"]
            if re.search(r"thường\s*trú|place\s*of\s*residence", t, re.IGNORECASE):
                recording_residence = True
                cleaned = re.sub(r".*?(thường\s*trú|residence)[:;]?", "", t, flags=re.IGNORECASE).strip()
                if cleaned:
                    residence_parts.append(cleaned)
                    residence_confs.append(box["confidence"])
                continue

            if recording_residence:
                dm = DATE_REGEX.search(t)
                if dm and not fields["date_of_expiry"]["value"]:
                    y = int(dm.group(3))
                    if y >= 2024:
                        fields["date_of_expiry"] = {
                            "value": f"{dm.group(1).zfill(2)}/{dm.group(2).zfill(2)}/{dm.group(3)}",
                            "confidence": box["confidence"]
                        }

                cleaned_box = clean_address(t)
                if cleaned_box:
                    residence_parts.append(cleaned_box)
                    residence_confs.append(box["confidence"])

                if re.search(r"^(có\s*giá\s*t[r|i|í]\s*đến|cógiá|tíđến|date\s*of\s*expiry|hết\s*hạn)", t.strip(), re.IGNORECASE) and not cleaned_box:
                    recording_residence = False
                    break

        if residence_parts:
            raw_res = ", ".join(residence_parts).replace(";,", ",")
            fields["place_of_residence"] = {
                "value": clean_address(raw_res),
                "confidence": round(sum(residence_confs) / len(residence_confs), 2)
            }

    elif side == "BACK":
        # 1. Identifying Features (Đặc điểm nhân dạng)
        features_parts = []
        features_confs = []
        recording_features = False

        for box in raw_boxes:
            t = box["text"]
            if re.search(r"đặc\s*điểm\s*nhân\s*dạng|personal\s*identification", t, re.IGNORECASE):
                recording_features = True
                cleaned = re.sub(r".*?(nhân\s*dạng|identification)[:;]?", "", t, flags=re.IGNORECASE).strip()
                if cleaned:
                    features_parts.append(cleaned)
                    features_confs.append(box["confidence"])
                continue

            if recording_features:
                if re.search(r"ngày|date|tháng|năm|cục\s*trưởng|công\s*an", t, re.IGNORECASE):
                    recording_features = False
                    break
                features_parts.append(t.strip())
                features_confs.append(box["confidence"])

        if features_parts:
            fields["identifying_features"] = {
                "value": clean_vietnamese_text(" ".join(features_parts)),
                "confidence": round(sum(features_confs) / len(features_confs), 2)
            }

        # 2. Date of Issue (Ngày cấp)
        for box in raw_boxes:
            t = box["text"]
            if re.search(r"ngày|date|month|year", t, re.IGNORECASE):
                m = DATE_REGEX.search(t)
                if m:
                    fields["date_of_issue"] = {"value": f"{m.group(1).zfill(2)}/{m.group(2).zfill(2)}/{m.group(3)}", "confidence": box["confidence"]}
                    break

        # 3. Issuing Authority
        authority_parts = []
        authority_confs = []
        for box in raw_boxes:
            t = box["text"]
            if re.search(r"cục\s*trưởng|giám\s*đốc|quản\s*lý\s*hành\s*chính|cảnh\s*sát|công\s*an", t, re.IGNORECASE):
                authority_parts.append(t.strip())
                authority_confs.append(box["confidence"])

        if authority_parts:
            fields["issuing_authority"] = {
                "value": clean_vietnamese_text(" - ".join(authority_parts)),
                "confidence": round(sum(authority_confs) / len(authority_confs), 2)
            }
        else:
            fields["issuing_authority"] = {
                "value": "CỤC TRƯỞNG CỤC CẢNH SÁT QUẢN LÝ HÀNH CHÍNH VỀ TRẬT TỰ XÃ HỘI",
                "confidence": 0.85
            }

        # 4. MRZ Code
        mrz_lines = []
        for box in raw_boxes:
            t = box["text"].replace(" ", "")
            if "<<" in t or (len(t) >= 28 and re.match(r"^[A-Z0-9<]+$", t)):
                mrz_lines.append(t)
        if mrz_lines:
            fields["mrz_code"] = {"value": "\n".join(mrz_lines), "confidence": 0.90}

    # Calculate overall confidence
    scores = [v["confidence"] for v in fields.values() if v.get("value") is not None and v.get("confidence", 0) > 0]
    overall_conf = round(sum(scores) / len(scores), 3) if scores else 0.50

    # Build warnings
    warnings = []
    if side == "FRONT":
        if not fields["id_number"]["value"]:
            warnings.append("Không trích xuất được số CCCD/CMND. Hãy kiểm tra góc chụp hoặc độ nét.")
        elif len(fields["id_number"]["value"]) not in (9, 12):
            warnings.append(f"Số giấy tờ ({fields['id_number']['value']}) không chuẩn 9 hoặc 12 chữ số.")
            
        if not fields["full_name"]["value"]:
            warnings.append("Không trích xuất được họ và tên. Vui lòng bổ sung thủ công.")

        # Check expiry
        exp = fields["date_of_expiry"]["value"]
        if exp and exp != "Không thời hạn":
            try:
                exp_date = datetime.strptime(exp, "%d/%m/%Y")
                if exp_date < datetime.now():
                    warnings.append(f"Thẻ CCCD đã hết hạn từ ngày {exp}.")
            except Exception:
                pass

    if overall_conf < 0.65:
        warnings.append("Độ tin cậy tổng thể thấp (< 65%). Bạn nên kiểm tra lại các trường thông tin.")

    return {
        "side": side,
        "document_type": doc_type,
        "fields": fields,
        "overall_confidence": overall_conf,
        "warnings": warnings
    }

def merge_front_and_back(front_res: Dict[str, Any], back_res: Dict[str, Any]) -> Dict[str, Any]:
    """Combines extracted data from both FRONT and BACK images into a single complete record."""
    combined_fields = {}
    # Start with front fields
    for k, v in front_res.get("fields", {}).items():
        combined_fields[k] = v

    # Overlay back side fields
    for k in ["date_of_issue", "issuing_authority", "identifying_features", "mrz_code"]:
        if back_res.get("fields", {}).get(k, {}).get("value"):
            combined_fields[k] = back_res["fields"][k]

    # Combine warnings
    all_warnings = front_res.get("warnings", []) + back_res.get("warnings", [])

    # Average confidence
    f_conf = front_res.get("overall_confidence", 0.0)
    b_conf = back_res.get("overall_confidence", 0.0)
    comb_conf = round((f_conf + b_conf) / 2.0, 3)

    return {
        "side": "BOTH",
        "document_type": front_res.get("document_type", "CCCD_CHIP"),
        "fields": combined_fields,
        "overall_confidence": comb_conf,
        "warnings": list(set(all_warnings))
    }
