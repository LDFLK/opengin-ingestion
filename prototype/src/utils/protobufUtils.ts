export function parseProtobufName(nameStr: string): { value: string; startTime: string; endTime: string } {
    try {
        // Handle case where name is already an object (if API changes)
        if (typeof nameStr === 'object') {
            return nameStr;
        }

        const parsed = JSON.parse(nameStr);

        // Decode hex value if present
        let decodedValue = parsed.value;
        if (parsed.value && /^[0-9A-Fa-f]+$/.test(parsed.value)) {
            try {
                // Convert hex to string
                decodedValue = Buffer.from(parsed.value, 'hex').toString('utf8');
            } catch (e) {
                console.warn("Failed to decode hex value:", parsed.value);
            }
        }

        return {
            value: decodedValue || "",
            startTime: parsed.startTime || "",
            endTime: parsed.endTime || ""
        };
    } catch (e) {
        console.warn("Failed to parse protobuf name string:", nameStr);
        // Fallback: return the string as value
        return {
            value: nameStr,
            startTime: "",
            endTime: ""
        };
    }
}
