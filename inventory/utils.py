from django.utils.translation import get_language
import arabic_reshaper
from bidi.algorithm import get_display

def transliterate_name(name, target_language=None):
    """
    Transliterates a name between Arabic and English based on the target language.
    If target_language is not provided, uses the current Django language setting.
    
    Args:
        name (str): The name to transliterate
        target_language (str, optional): The target language code ('ar' or 'en')
    
    Returns:
        str: The transliterated name
    """
    if not name:
        return name
        
    if target_language is None:
        target_language = get_language()
    
    # If the name is already in the target language, return it as is
    if (target_language == 'ar' and any('\u0600' <= c <= '\u06FF' for c in name)) or \
       (target_language == 'en' and not any('\u0600' <= c <= '\u06FF' for c in name)):
        return name
    
    # Arabic to English transliteration mapping
    arabic_to_english = {
        'ا': 'a', 'أ': 'a', 'إ': 'e', 'آ': 'a', 'ى': 'a',
        'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h',
        'خ': 'kh', 'د': 'd', 'ذ': 'th', 'ر': 'r', 'ز': 'z',
        'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't',
        'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
        'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h',
        'و': 'w', 'ي': 'y', 'ة': 'h', 'ئ': 'y', 'ء': 'a',
        ' ': ' ', '-': '-', '_': '_'
    }
    
    # English to Arabic transliteration mapping
    english_to_arabic = {
        'a': 'ا', 'b': 'ب', 'c': 'ك', 'd': 'د', 'e': 'ي',
        'f': 'ف', 'g': 'ج', 'h': 'ه', 'i': 'ي', 'j': 'ج',
        'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن', 'o': 'و',
        'p': 'ب', 'q': 'ق', 'r': 'ر', 's': 'س', 't': 'ت',
        'u': 'و', 'v': 'ف', 'w': 'و', 'x': 'كس', 'y': 'ي',
        'z': 'ز', ' ': ' ', '-': '-', '_': '_'
    }
    
    if target_language == 'ar':
        # English to Arabic transliteration
        result = ''
        for char in name.lower():
            result += english_to_arabic.get(char, char)
        # Reshape Arabic text for proper display
        reshaped_text = arabic_reshaper.reshape(result)
        return get_display(reshaped_text)
    else:
        # Arabic to English transliteration
        result = ''
        for char in name:
            result += arabic_to_english.get(char, char)
        return result.capitalize()

def format_name_for_display(name):
    """
    Formats a name for display based on the current language setting.
    Handles both Arabic and English names appropriately.
    
    Args:
        name (str): The name to format
    
    Returns:
        str: The formatted name
    """
    current_language = get_language()
    
    if current_language == 'ar':
        # If the name is in English, transliterate it to Arabic
        if not any('\u0600' <= c <= '\u06FF' for c in name):
            return transliterate_name(name, 'ar')
        # If the name is already in Arabic, reshape it for proper display
        reshaped_text = arabic_reshaper.reshape(name)
        return get_display(reshaped_text)
    else:
        # If the name is in Arabic, transliterate it to English
        if any('\u0600' <= c <= '\u06FF' for c in name):
            return transliterate_name(name, 'en')
        return name 