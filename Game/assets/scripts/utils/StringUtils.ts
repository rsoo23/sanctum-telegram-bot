
// isTrailing: if true, it adds a ... behind the trimmed string
function trimString( 
    str: string, 
    maxLength: number, 
    isTrailing: boolean = true
): string {
    if (str.length <= maxLength) return str;

    if (isTrailing) {
        return str.substring(0, maxLength) + "...";
    } else {
        return str.substring(0, maxLength);
    }
}

export { trimString }
