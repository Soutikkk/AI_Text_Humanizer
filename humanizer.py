"""
AI Text Humanizer Engine
Provides functions to convert formal, repetitive, or robotic AI-generated text
into natural, conversational human-like text.
"""

import re
import random
import json
import urllib.request
import urllib.error

# NLTK initialization and fallback check
_nltk_available = False
try:
    import nltk
    from nltk.corpus import wordnet
    # Try to access wordnet; if not loaded, attempt download
    try:
        wordnet.synsets("test")
        _nltk_available = True
    except (LookupError, AttributeError):
        # Programmatically download without blocking
        nltk.download("wordnet", quiet=True)
        nltk.download("omw-1.4", quiet=True)
        wordnet.synsets("test")
        _nltk_available = True
except Exception:
    _nltk_available = False

# List of common English stop words to ignore during word frequency checks
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "because", "as", "until", "while",
    "of", "at", "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out",
    "on", "off", "over", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "i", "me",
    "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
    "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it",
    "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which",
    "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing",
    "would", "should", "could", "ought", "i'm", "you're", "he's", "she's", "it's", "we're",
    "they're", "i've", "you've", "we've", "they've", "i'd", "you'd", "he'd", "she'd",
    "we'd", "they'd", "i'll", "you'll", "he'll", "she'll", "we'll", "they'll", "isn't",
    "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't", "doesn't", "don't",
    "didn't", "won't", "wouldn't", "shan't", "shouldn't", "can't", "cannot", "couldn't",
    "mustn't", "let's", "that's", "who's", "what's", "here's", "there's", "when's",
    "where's", "why's", "how's"
}

# Formal to informal contractions mapping
CONTRACTIONS = {
    "is not": "isn't",
    "cannot": "can't",
    "do not": "don't",
    "does not": "doesn't",
    "will not": "won't",
    "would not": "wouldn't",
    "should not": "shouldn't",
    "could not": "couldn't",
    "are not": "aren't",
    "was not": "wasn't",
    "were not": "weren't",
    "have not": "haven't",
    "has not": "hasn't",
    "had not": "hadn't",
    "did not": "didn't",
    "i am": "i'm",
    "you are": "you're",
    "we are": "we're",
    "they are": "they're",
    "it is": "it's",
    "he is": "he's",
    "she is": "she's",
    "that is": "that's",
    "there is": "there's",
    "what is": "what's",
    "who is": "who's",
    "i will": "i'll",
    "you will": "you'll",
    "we will": "we'll",
    "they will": "they'll",
    "it will": "it'll",
    "he will": "he'll",
    "she will": "she'll",
    "i would": "i'd",
    "you would": "you'd",
    "we would": "we'd",
    "they would": "they'd",
    "he would": "he'd",
    "she would": "she'd",
    "i have": "i've",
    "you have": "you've",
    "we have": "we've",
    "they have": "they've",
}

# Robotic or overly formal phrase mapping
ROBOTIC_PHRASES = {
    "in order to": "to",
    "utilize": "use",
    "utilizes": "uses",
    "utilizing": "using",
    "utilization": "use",
    "furthermore": "also",
    "moreover": "what's more",
    "consequently": "so",
    "subsequently": "then",
    "subsequent to": "after",
    "in conclusion": "overall",
    "to conclude": "lastly",
    "it is important to note that": "note that",
    "it is crucial to": "we need to",
    "it should be pointed out that": "actually,",
    "notwithstanding the fact that": "even though",
    "due to the fact that": "because",
    "in the event that": "if",
    "at this point in time": "now",
    "demonstrate": "show",
    "demonstrates": "shows",
    "demonstrated": "showed",
    "demonstrating": "showing",
    "additionally": "plus",
    "on the other hand": "but then",
    "nevertheless": "still",
    "nonetheless": "even so",
    "first and foremost": "first",
    "in terms of": "when it comes to",
    "with respect to": "about",
    "regarding": "about",
    "concerning": "about",
    "as a consequence of": "because of",
    "a wide range of": "many",
    "a vast majority of": "most",
    "conduct an analysis of": "analyze",
    "provide assistance to": "help",
    "is indicative of": "shows",
    "at the present time": "currently",
    "elucidate": "explain",
    "elucidated": "explained",
    "elucidates": "explains",
    "elucidating": "explaining",
    "facilitate": "help",
    "facilitates": "helps",
    "facilitating": "helping",
    "facilitated": "helped",
    "endeavor": "try",
    "endeavored": "tried",
    "endeavors": "tries",
    "endeavoring": "trying",
    "predominantly": "mostly",
    "commence": "start",
    "commences": "starts",
    "commenced": "started",
    "commencing": "starting",
    "terminate": "end",
    "terminates": "ends",
    "terminated": "ended",
    "terminating": "ending",
}

# Built-in synonym dictionary for fallback
BUILTIN_SYNONYMS = {
    "very": ["extremely", "highly", "really", "incredibly", "super"],
    "good": ["excellent", "great", "fine", "decent", "superb"],
    "bad": ["poor", "terrible", "awful", "unpleasant", "faulty"],
    "important": ["crucial", "essential", "key", "vital", "significant"],
    "make": ["create", "build", "produce", "generate", "craft"],
    "show": ["display", "reveal", "indicate", "present", "point out"],
    "use": ["employ", "apply", "adopt", "harness"],
    "many": ["numerous", "plentiful", "a lot of", "several", "various"],
    "change": ["modify", "alter", "transform", "adjust", "shift"],
    "help": ["assist", "support", "guide", "aid"],
    "think": ["believe", "reckon", "consider", "feel", "imagine"],
    "say": ["state", "mention", "declare", "remark", "express"],
    "quick": ["fast", "rapid", "swift", "speedy", "prompt"],
    "slow": ["sluggish", "leisurely", "gradual", "deliberate"],
    "happy": ["glad", "cheerful", "delighted", "pleased", "joyful"],
    "sad": ["gloomy", "unhappy", "depressed", "sorrowful", "down"],
    "new": ["fresh", "modern", "novel", "recent", "innovative"],
    "old": ["ancient", "aged", "antique", "mature", "outdated"],
    "problem": ["issue", "challenge", "difficulty", "trouble", "obstacle"],
    "solution": ["answer", "remedy", "resolution", "way out"],
    "people": ["individuals", "folks", "humans", "the public"],
    "work": ["labor", "task", "job", "effort", "activity"],
    "small": ["tiny", "little", "minor", "slight"],
    "large": ["huge", "big", "massive", "giant", "substantial"],
    "difficult": ["hard", "challenging", "tough", "demanding"],
    "easy": ["simple", "effortless", "straightforward", "light"],
}

# Human filler transitions for High strength humanization
CONVERSATIONAL_TRANSITIONS = [
    "Well, ",
    "Actually, ",
    "To be honest, ",
    "Basically, ",
    "Honestly, ",
    "You see, ",
    "As it turns out, ",
]


def is_word(token):
    """Checks if a string token is a valid word (allowing inline contractions)."""
    return bool(re.match(r"^[a-zA-Z]+(?:'[a-zA-Z]+)?$", token))


def get_synonyms(word):
    """
    Retrieves synonyms for a given word using NLTK WordNet if available,
    falling back to or combining with a built-in synonym dictionary.
    """
    word_lower = word.lower()
    synonyms = []

    # 1. Try NLTK WordNet
    if _nltk_available:
        try:
            for synset in wordnet.synsets(word_lower):
                for lemma in synset.lemmas():
                    name = lemma.name().replace('_', ' ').replace('-', ' ')
                    # Avoid adding duplicates or the word itself
                    if name.lower() != word_lower and name not in synonyms:
                        synonyms.append(name)
        except Exception:
            pass

    # 2. Integrate built-in synonyms
    if word_lower in BUILTIN_SYNONYMS:
        for syn in BUILTIN_SYNONYMS[word_lower]:
            if syn not in synonyms:
                synonyms.append(syn)

    return synonyms


def replace_repetitive_words(text):
    """
    Replaces repeated occurrences of high-frequency words with synonyms.
    Only replaces words that appear 3 or more times, ignoring standard stop words.
    Preserves casing and formatting.
    """
    if not text.strip():
        return text

    # Tokenize text, separating words (including apostrophes) and non-word sequences (punctuation, whitespace)
    tokens = re.split(r"([a-zA-Z]+(?:'[a-zA-Z]+)?)", text)
    
    word_counts = {}
    word_indices = []

    # First pass: count word occurrences (ignoring stop words)
    for idx, token in enumerate(tokens):
        if token and is_word(token):
            word_lower = token.lower()
            if word_lower not in STOP_WORDS:
                word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
                word_indices.append((idx, word_lower))

    # A word is a candidate for replacement if it's repeated >= 2 times
    repeated_candidates = {word for word, count in word_counts.items() if count >= 2}

    # Second pass: replace subsequent occurrences
    seen_counts = {}
    for idx, word_lower in word_indices:
        seen_counts[word_lower] = seen_counts.get(word_lower, 0) + 1
        
        # If we have seen this repeated word before, substitute it
        if word_lower in repeated_candidates and seen_counts[word_lower] > 1:
            syns = get_synonyms(word_lower)
            if syns:
                # Cycle through synonyms deterministically
                syn = syns[(seen_counts[word_lower] - 2) % len(syns)]
                
                # Match casing of the original word
                original_word = tokens[idx]
                if original_word.istitle():
                    syn = syn.title()
                elif original_word.isupper():
                    syn = syn.upper()
                
                tokens[idx] = syn

    return "".join(tokens)


def improve_sentence_flow(text, strength="Medium"):
    """
    Varies sentence structure and improves natural reading flow.
    - Replaces robotic, formal phrases with natural ones.
    - Contracts phrases at Medium/High strength.
    - Splits overly long sentences (conjunction splits).
    - Introduces human-like conversational transitions at High strength.
    """
    if not text.strip():
        return text

    # Define thresholds based on strength
    # Low: 40% replacement chance, no sentence splits, no conversational filler
    # Medium: 75% replacement chance, moderate sentence splits, no conversational filler
    # High: 100% replacement chance, aggressive sentence splits, conversational fillers
    prob_replacement = 0.4 if strength == "Low" else (0.75 if strength == "Medium" else 1.0)
    
    # 1. Robotic phrase replacements
    for robotic, natural in ROBOTIC_PHRASES.items():
        pattern = r'\b' + re.escape(robotic) + r'\b'
        
        def replace_phrase(match):
            if random.random() > prob_replacement:
                return match.group(0)
                
            matched_text = match.group(0)
            # Match capitalization (e.g. "Furthermore" -> "Also")
            if matched_text and matched_text[0].isupper():
                return natural[0].upper() + natural[1:] if len(natural) > 1 else natural.upper()
            return natural

        text = re.sub(pattern, replace_phrase, text, flags=re.IGNORECASE)

    # 2. Contractions (only for Medium and High strength)
    if strength in ("Medium", "High"):
        for formal, contracted in CONTRACTIONS.items():
            pattern = r'\b' + re.escape(formal) + r'\b'
            
            def replace_contraction(match):
                matched_text = match.group(0)
                if matched_text.istitle():
                    return contracted.title()
                elif matched_text.isupper():
                    return contracted.upper()
                return contracted

            text = re.sub(pattern, replace_contraction, text, flags=re.IGNORECASE)

    # 3. Sentence Splitting (Medium/High)
    if strength in ("Medium", "High") and len(text.split()) > 15:
        # Split sentences by . ! ? while preserving punctuation and spaces
        sentence_parts = re.split(r'(\s*[\.\!\?]+\s*)', text)
        for i in range(0, len(sentence_parts), 2):
            sentence = sentence_parts[i]
            words = sentence.split()
            # If a sentence is long (e.g. > 20 words), try to split on coordinating conjunctions
            if len(words) > 20:
                match = re.search(r',\s+(and|but|or|so)\s+', sentence, flags=re.IGNORECASE)
                if match:
                    start, end = match.span()
                    part1 = sentence[:start] + "."
                    part2 = sentence[end:]
                    if part2:
                        part2 = part2[0].upper() + part2[1:]
                    sentence_parts[i] = part1 + " " + part2
        text = "".join(sentence_parts)

    # 4. Inject human filler transitions (High strength only)
    if strength == "High":
        sentence_parts = re.split(r'(\s*[\.\!\?]+\s*)', text)
        # We start from index 2 to avoid prepending a filler to the absolute first sentence
        for i in range(2, len(sentence_parts), 2):
            sentence = sentence_parts[i]
            if len(sentence.strip()) > 10 and not sentence.startswith(" ") and random.random() < 0.15:
                # Add conversational filler at beginning
                filler = random.choice(CONVERSATIONAL_TRANSITIONS)
                # Ensure the current sentence doesn't already start with a capital/filler word structure
                first_word = sentence.split()[0].rstrip(",.!?").lower() if sentence.split() else ""
                if first_word not in ["well", "actually", "honestly", "basically", "but", "however", "and", "so"]:
                    # De-capitalize the original first letter of the sentence
                    decapped = sentence[0].lower() + sentence[1:] if len(sentence) > 0 else sentence
                    sentence_parts[i] = filler + decapped
        text = "".join(sentence_parts)

    return text


def humanize_text_openai(text, api_key, strength="Medium"):
    """
    Rewrites the text using OpenAI Chat Completions API.
    Sends raw HTTP requests via standard library urllib to avoid extra dependencies.
    """
    if not api_key:
        raise ValueError("OpenAI API Key is required.")
    if not text.strip():
        return text

    # Strength prompts configuration
    strength_prompts = {
        "Low": (
            "Slightly rewrite the following text to sound more natural. "
            "Make minimal changes, just fix robotic phrasing and repetitive vocabulary. "
            "Keep the original structure."
        ),
        "Medium": (
            "Rewrite the following text to sound human and conversational. "
            "Remove common AI writing patterns (e.g., overly structured paragraphs, repeating transitions). "
            "Vary sentence lengths and use moderate contractions."
        ),
        "High": (
            "Aggressively rewrite the following text to sound highly human, casual, and engaging. "
            "Introduce sentence flow variations, conversational transitions, appropriate contractions, "
            "and natural vocabulary. Ensure it bypasses typical AI detectors while preserving the core meaning."
        )
    }

    prompt = strength_prompts.get(strength, strength_prompts["Medium"])
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert copywriter. Your task is to humanize AI-generated text, "
                    "making it flow naturally, sound conversational, and read like it was written "
                    "by an experienced human writer. Preserve the original meaning exactly."
                )
            },
            {"role": "user", "content": f"{prompt}\n\nText to humanize:\n{text}"}
        ],
        "temperature": 0.7 if strength == "Medium" else (0.5 if strength == "Low" else 0.9)
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        try:
            error_json = json.loads(error_msg)
            raise RuntimeError(f"OpenAI API Error: {error_json['error']['message']}")
        except Exception:
            raise RuntimeError(f"OpenAI API HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Network error contacting OpenAI: {str(e)}")


def humanize_text(text, strength="Medium", method="local", openai_api_key=None):
    """
    Main orchestrator function for humanizing text.
    Handles empty/blank input text gracefully.
    
    Parameters:
    - text (str): The input text to humanize.
    - strength (str): Low, Medium, or High.
    - method (str): 'local' or 'openai'.
    - openai_api_key (str): Optional OpenAI API key when method is 'openai'.
    """
    if not text or not text.strip():
        return ""

    if method == "openai":
        return humanize_text_openai(text, openai_api_key, strength)
    
    # Local Humanizer Pipeline:
    # 1. Robotic transitions and structural improvements
    processed = improve_sentence_flow(text, strength)
    # 2. Replace repetitive vocabulary with synonyms
    processed = replace_repetitive_words(processed)
    
    return processed
