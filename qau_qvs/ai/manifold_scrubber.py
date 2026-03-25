import re

class ManifoldScrubber:
    """
    Manifold Scrubber: Phase XXXVIII - Textual Sanctity.
    Cleans raw PDF/Wiki payloads, fixes encoding errors, 
    and ensures full-sentence integrity.
    """
    
    @staticmethod
    def clean_payload(text: str) -> str:
        # 1. Fix Encoding and non-ascii artifacts (Force ASCII)
        text = text.encode("ascii", "ignore").decode("ascii")
        
        # 2. Normalize whitespace and linebreaks
        text = text.replace("- ", "").replace("\n", " ") # joins hyphenated-words from PDF
        text = re.sub(r'\s+', ' ', text)
        
        # 3. Fix typical PDF-extraction spacing errors (e.g. 'L a w' or 'I r r')
        # We look for single letters separated by single spaces and join them
        text = re.sub(r'(?<= )([a-z]) (?=[a-z] )', r'\1', text, flags=re.IGNORECASE)
        
        return text.strip()

    @staticmethod
    def extract_definition(text: str, keywords: list) -> str:
        """Isolated Thinking: Finds the most 'definitional' and descriptive sentence."""
        sentences = [s.strip() for s in text.split('.') if len(s) > 40]
        # Patterns that suggest a real explanation, NOT a chapter title
        patterns = [r"is\s+(based|defined|built|driven|motivated)", r"means\s+that", r"refers\s+to", r"states\s+that"]
        
        candidates = []
        for s in sentences:
            if any(k in s.lower() for k in keywords):
                # Score the sentence based on descriptive verbs and length
                score = sum(3 for p in patterns if re.search(p, s.lower()))
                if len(s) > 100: score += 1
                if s.count(" ") > 15: score += 1 # Punctuation/complexity density
                candidates.append((score, s))
        
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1] + "."
            
        return (sentences[0] + ".") if sentences else "Concept unverifiable."

    @staticmethod
    def extract_advice(text: str, keywords: list) -> str:
        """Isolated Thinking: Finds actionable advice or 'how-to' sentences."""
        sentences = [s.strip() for s in text.split('.') if len(s) > 40]
        advice_words = ["must", "should", "learn", "how", "strategy", "try", "avoid"]
        
        for s in sentences:
            if any(k in s.lower() for k in keywords):
                if any(aw in s.lower() for aw in advice_words):
                    return s + "."
        return "Observe internal manifold for action."
