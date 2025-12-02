import { NextRequest, NextResponse } from "next/server";

// Separate READ and INGESTION API URLs
const READ_API_URL = process.env.OPENGIN_READ_API_URL || "http://0.0.0.0:8081";
const INGESTION_API_URL = process.env.OPENGIN_INGESTION_API_URL || "http://0.0.0.0:8080";

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await params;
        // GET by ID uses READ API with POST to /v1/entities/search
        // Note: Search by ID using POST with payload, not GET
        const response = await fetch(`${READ_API_URL}/v1/entities/search`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                id: id  // Search by ID
            }),
        });

        if (!response.ok) {
            return NextResponse.json(
                { error: `Backend API error: ${response.statusText}` },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error fetching entity:", error);
        return NextResponse.json(
            { error: "Failed to fetch entity" },
            { status: 500 }
        );
    }
}

export async function PUT(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await params;
        const body = await request.json();

        // PUT uses INGESTION API for updating entities
        const response = await fetch(`${INGESTION_API_URL}/entities/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Backend API error:", response.status, errorText);
            return NextResponse.json(
                { error: `Backend API error: ${response.statusText}`, details: errorText },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error updating entity:", error);
        return NextResponse.json(
            { error: "Failed to update entity" },
            { status: 500 }
        );
    }
}
