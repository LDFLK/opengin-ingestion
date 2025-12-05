import { NextRequest, NextResponse } from "next/server";

// Separate READ and INGESTION API URLs
const READ_API_URL = process.env.OPENGIN_READ_API_URL || "http://0.0.0.0:8081";
const INGESTION_API_URL = process.env.OPENGIN_INGESTION_API_URL || "http://0.0.0.0:8080";

export async function GET() {
    try {
        // TODO: NOT FUNCTIONAL PLEASE IMPLEMENT IN OpenGIN or figure out an alternative. 
        // NOTE: There is no such endpoint in OpenGin yet. This is something we must think of adding.
        // GET uses READ API - not typically used for listing all entities
        // This endpoint might not be needed if we only search by kind
        const response = await fetch(`${READ_API_URL}/entities`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
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
        console.error("Error fetching entities:", error);
        return NextResponse.json(
            { error: "Failed to fetch entities" },
            { status: 500 }
        );
    }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // POST uses INGESTION API for creating entities
        const response = await fetch(`${INGESTION_API_URL}/entities`, {
            method: "POST",
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
        console.error("Error creating entity:", error);
        return NextResponse.json(
            { error: "Failed to create entity" },
            { status: 500 }
        );
    }
}
