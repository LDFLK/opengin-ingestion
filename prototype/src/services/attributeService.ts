export interface AttributeValue {
    columns: string[];
    rows: Record<string, string>[];
}

export interface Attribute {
    id: string;
    name: string;
    value: AttributeValue;
    startTime: string;
    endTime: string;
}

let mockAttributes: Attribute[] = [
    {
        id: "a1",
        name: "Monthly Expenses",
        value: {
            columns: ["Category", "Amount", "Payment Method", "Notes"],
            rows: [
                { Category: "Rent", Amount: "$2,500", "Payment Method": "Bank Transfer", Notes: "Apartment 4B" },
                { Category: "Utilities", Amount: "$180", "Payment Method": "Auto-Pay", Notes: "Electric, Water, Gas" },
                { Category: "Groceries", Amount: "$650", "Payment Method": "Credit Card", Notes: "Weekly shopping" },
                { Category: "Transportation", Amount: "$120", "Payment Method": "Debit Card", Notes: "Gas and parking" },
                { Category: "Internet", Amount: "$80", "Payment Method": "Auto-Pay", Notes: "100 Mbps plan" },
            ],
        },
        startTime: "2024-01-01T00:00",
        endTime: "2024-01-31T23:59",
    },
    {
        id: "a2",
        name: "Customer Orders",
        value: {
            columns: ["Order ID", "Customer", "Product", "Quantity", "Total", "Status"],
            rows: [
                { "Order ID": "ORD-1001", Customer: "Alice Johnson", Product: "Laptop", Quantity: "1", Total: "$1,299", Status: "Shipped" },
                { "Order ID": "ORD-1002", Customer: "Bob Smith", Product: "Mouse", Quantity: "3", Total: "$89.97", Status: "Delivered" },
                { "Order ID": "ORD-1003", Customer: "Carol White", Product: "Keyboard", Quantity: "2", Total: "$239.98", Status: "Processing" },
                { "Order ID": "ORD-1004", Customer: "David Brown", Product: "Monitor", Quantity: "1", Total: "$449", Status: "Pending" },
            ],
        },
        startTime: "2024-02-01T00:00",
        endTime: "2024-02-28T23:59",
    },
    {
        id: "a3",
        name: "Inventory Levels",
        value: {
            columns: ["Product SKU", "Product Name", "Quantity", "Location", "Reorder Level"],
            rows: [
                { "Product SKU": "TECH-001", "Product Name": "Wireless Mouse", Quantity: "45", Location: "Warehouse A", "Reorder Level": "20" },
                { "Product SKU": "TECH-002", "Product Name": "USB-C Cable", Quantity: "12", Location: "Warehouse B", "Reorder Level": "30" },
                { "Product SKU": "TECH-003", "Product Name": "Laptop Stand", Quantity: "67", Location: "Warehouse A", "Reorder Level": "15" },
                { "Product SKU": "TECH-004", "Product Name": "Webcam HD", Quantity: "8", Location: "Warehouse C", "Reorder Level": "25" },
            ],
        },
        startTime: "2024-03-01T00:00",
        endTime: "",
    },
];

export const attributeService = {
    getAttributes: async (): Promise<Attribute[]> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return [...mockAttributes];
    },

    createAttribute: async (attribute: Attribute): Promise<Attribute> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        mockAttributes.push(attribute);
        return attribute;
    },

    getAttributesByName: async (name: string): Promise<Attribute[]> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return mockAttributes.filter((a) => a.name === name);
    },

    getAttributeById: async (id: string): Promise<Attribute | undefined> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return mockAttributes.find((a) => a.id === id);
    },

    updateAttribute: async (attribute: Attribute): Promise<Attribute> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        const index = mockAttributes.findIndex((a) => a.id === attribute.id);
        if (index !== -1) {
            mockAttributes[index] = attribute;
            return attribute;
        }
        throw new Error("Attribute not found");
    },
};
