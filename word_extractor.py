from textblob import TextBlob

def word_extractor(text, keyword, n):
    text = (TextBlob(text.lower())).words
    #print(text)
    ndx = []
    obama_list = []
    for i, j in enumerate(text):
        '''creates list of indexes at which the keyword obama appears'''
        if j == keyword:
            ndx.append(i)
            #print(ndx)

    if len(ndx) == 0:
        '''for emails that do not contain the word obama'''
        obama_text = None
        return obama_text

    if len(ndx) == 1:
        '''for emails with 1 occurence of obama'''
        for i, j in enumerate(ndx):
            obama_list.append(' '.join(text[(j-n):j] + text[j:(j+n)]))

    elif len(ndx) == 2:
        '''for emails with 2 occurences of obama'''
        diff = (ndx[1] - ndx[0])/2
        if diff < (n*2):
            obama_list.append(' '.join(text[(ndx[0]-n):ndx[0]] + text[ndx[0]:ndx[1]] + text[ndx[1]:(ndx[1]+n)]))
        else:
            obama_list.append(' '.join(text[(ndx[0]-n):ndx[0]] + text[ndx[0]:(ndx[0]+n)] + text[(ndx[1]-n):ndx[1]] + text[ndx[1]:(ndx[1]+n)]))

    else:
        '''for emails with 3+ occurences of obama'''
        for i, j in enumerate(ndx):
            if i == 0:
                diff = (ndx[i+1] - ndx[i])/2
                if diff < (n*2):
                    obama_list.append(' '.join(text[(ndx[0]-n):ndx[0]] + text[ndx[0]:(ndx[0]+diff)]))
                else:
                    obama_list.append(' '.join(text[(ndx[0]-n):ndx[0]] + text[ndx[0]:(ndx[0]+n)]))
            elif (i + 1) == len(ndx):
                diff = (ndx[i] - ndx[i-1])/2
                if diff < (n*2):
                    obama_list.append(' '.join(text[(ndx[-1]-diff):ndx[-1]] + text[ndx[-1]:(ndx[-1]+diff)]))
                else:
                    obama_list.append(' '.join(text[(ndx[-1]-n):ndx[-1]] + text[ndx[-1]:(ndx[-1]+n)]))
            else:
                front_diff = ndx[i] - ndx[i-1]
                back_diff = ndx[i+1] - ndx[i]
                if front_diff < (n*2) and back_diff < (n*2):
                    obama_list.append(' '.join(text[(ndx[i]-front_diff):ndx[i]] + text[ndx[i]:(ndx[i]+back_diff)]))
                elif front_diff < (n*2) and back_diff > (n*2):
                    obama_list.append(' '.join(text[(ndx[i]-front_diff):ndx[i]] + text[ndx[i]:(ndx[i]+n)]))
                elif front_diff > (n*2) and back_diff < (n*2):
                    obama_list.append(' '.join(text[(ndx[i]-n):ndx[i]] + text[ndx[i]:(ndx[i]+back_diff)]))
                else:
                    obama_list.append(' '.join(text[(ndx[i]-n):ndx[i]] + text[ndx[i]:(ndx[i]+n)]))

    obama_text = ''.join(obama_list)
    return obama_text
