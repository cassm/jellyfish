def fadeDownTo(fromVal, toVal, step):
    result = [0.0, 0.0, 0.0]

    for colour in range(3):
        if fromVal[colour] != toVal[colour]:
            diff = fromVal[colour] - toVal[colour]
            result[colour] = fromVal[colour] - diff*step
        else:
            result[colour] = toVal[colour]

    return tuple(result)
