import { NextRequest, NextResponse } from "next/server";

// READ API URL - used for searching entities
const READ_API_URL = process.env.OPENGIN_READ_API_URL || "http://0.0.0.0:8081";

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Forward search request to READ API
        const response = await fetch(`${READ_API_URL}/v1/entities/search`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        // 404 means no entities of this kind - return empty array
        if (response.status === 404) {
            return NextResponse.json([]);
        }

        if (!response.ok) {
            console.error("READ API error:", response.status, response.statusText);
            return NextResponse.json(
                { error: `Backend API error: ${response.statusText}` },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error searching entities:", error);
        return NextResponse.json(
            { error: "Failed to search entities" },
            { status: 500 }
        );
    }
}
