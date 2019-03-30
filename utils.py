def text_contains(text, keywords, series=False):
    if series:
        idx = 0
        for keyword in keywords:
            new_idx = text.find(keyword)
            if new_idx < idx:
                return False
            idx = new_idx
        return True
    
    for keyword in keywords:
        if (text.find(keyword) == -1):
            return False
    return True
