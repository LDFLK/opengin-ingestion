import { parseEntityResponse } from '../responseUtils';

describe('parseEntityResponse', () => {
    it('returns data for standard array response', () => {
        const data = [{ id: '1' }, { id: '2' }];
        expect(parseEntityResponse(data)).toEqual(data);
    });

    it('returns null for empty array response', () => {
        const data: any[] = [];
        expect(parseEntityResponse(data)).toBeNull();
    });

    it('returns body for wrapped response { body: [...] }', () => {
        const data = { body: [{ id: '1' }] };
        expect(parseEntityResponse(data)).toEqual(data.body);
    });

    it('returns null for empty wrapped response { body: [] }', () => {
        const data = { body: [] };
        expect(parseEntityResponse(data)).toBeNull();
    });

    it('returns original data if structure is unrecognized', () => {
        const data = { some: 'object' };
        expect(parseEntityResponse(data)).toEqual(data);
    });

    it('returns null for null/undefined input', () => {
        expect(parseEntityResponse(null)).toBeNull();
        expect(parseEntityResponse(undefined)).toBeNull();
    });
});
