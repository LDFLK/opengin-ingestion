export function parseEntityResponse(data: any): any[] | null {
    if (data === null || data === undefined) {
        return null;
    }

    // Handle { body: [] } or { body: [...] } shape
    if (data && typeof data === 'object' && 'body' in data && Array.isArray(data.body)) {
        if (data.body.length === 0) {
            return null;
        }
        return data.body;
    }

    // Handle standard array response
    if (Array.isArray(data)) {
        if (data.length === 0) {
            return null;
        }
        return data;
    }

    return data;
}
