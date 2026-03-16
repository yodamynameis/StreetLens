import re
from utils import logger


class InformationExtractor:
    def __init__(self):

        # Regex patterns
        self.email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

        # Phone pattern (handles +91, spaces, dashes)
        self.phone_pattern = re.compile(r'\b(?:\+91[\-\s]?|0)?[6-9]\d{4}[\-\s]?\d{5}\b')

        self.gst_pattern = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d][Z][A-Z\d]\b')

        self.website_pattern = re.compile(r'\b(?:https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')

        self.time_pattern = re.compile(
            r'\b(?:1[0-2]|0?[1-9])(?::[0-5][0-9])?\s?(?:AM|PM|am|pm)\b'
        )

        # Keywords likely to appear in shop names
        self.shop_keywords = [
            'store','traders','medical','electronics','mart',
            'bakery','salon','enterprises','bhojnalay',
            'corporation','general','supermarket','pharmacy',
            'clinic','chemist','drugs','restaurant','hotel',
            'cafe','dhaba','food','mobile','computer','gadgets',
            'appliances','cake','sweets','confectionery',
            'beauty','parlour','hair','spa','saloon','garments','clothing','footwear','books','stationery','furniture','decor','grocery','provision','hardware','tools','auto','accessories','jewellery','gift','toys','sports','fitness','gym','yoga','wellness'
        ]

        # Words that should NOT be treated as shop names
        self.ignore_shop_words = [
            "gstin","since","phone","mob","mobile","tel",
            "contact","www","http","email"
        ]

        # Address indicators
        self.address_keywords = [
            'road','street','sector','scheme','nagar','colony','marg',
            'near','opp','market','complex','building','lane',
            'block','chowk','shop','no'
        ]

    def extract_fields(self, text_lines):

        # -------- CLEAN OCR LINES --------
        clean_lines = []

        for line in text_lines:
            line = line.replace(")", "").replace("_", "").strip()

            if line:
                clean_lines.append(line)

        data = {
            "shop_name": "NA",
            "phone_number": "NA",
            "email": "NA",
            "address": "NA",
            "gst_number": "NA",
            "website": "NA",
            "opening_time": "NA",
            "closing_time": "NA"
        }

        full_text = " ".join(clean_lines)

        # -------- PHONE EXTRACTION --------
        phones = []
        matches = self.phone_pattern.findall(full_text)

        for num in matches:

            logger.info(f"Phone identified: {num}")

            digits = re.sub(r'\D', '', num)

            # Remove country code
            if digits.startswith("91") and len(digits) == 12:
                digits = digits[2:]

            if len(digits) == 10:
                phones.append(digits)

        if phones:
            data["phone_number"] = list(set(phones))

        # -------- EMAIL --------
        match = self.email_pattern.search(full_text)
        if match:
            data["email"] = match.group()

        # -------- GST --------
        match = self.gst_pattern.search(full_text)
        if match:
            data["gst_number"] = match.group()

        # -------- WEBSITE --------
        match = self.website_pattern.search(full_text)
        if match:
            data["website"] = match.group()

        # -------- OPENING/CLOSING TIME --------
        times_found = self.time_pattern.findall(full_text)

        if len(times_found) >= 1:
            data["opening_time"] = times_found[0].upper()

        if len(times_found) >= 2:
            data["closing_time"] = times_found[1].upper()

        # -------- SHOP NAME & ADDRESS --------
        candidate_names = []

        for line in clean_lines:

            line_lower = line.lower()

            # Detect address
            if data["address"] == "NA" and any(kw in line_lower for kw in self.address_keywords):
                data["address"] = line
                continue

            # Ignore metadata lines
            if any(word in line_lower for word in self.ignore_shop_words):
                continue

            # Keyword-based shop detection
            if data["shop_name"] == "NA" and any(kw in line_lower for kw in self.shop_keywords):
                data["shop_name"] = line
                continue

            # Collect candidate shop names
            letters = sum(c.isalpha() for c in line)
            ratio = letters / max(len(line), 1)

            if 5 <= len(line) <= 40 and ratio > 0.6:
             candidate_names.append(line)

        # Choose best candidate
        if data["shop_name"] == "NA" and candidate_names:
            data["shop_name"] = max(candidate_names, key=len)

        # Final fallback
        if data["shop_name"] == "NA" and clean_lines:
            data["shop_name"] = clean_lines[0]

        return data