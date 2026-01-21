"use client";

import { Activity } from "lucide-react";
import GraphViz from "@/features/xplore/components/GraphViz";

export default function XplorePage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Xplore</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Visualize entity relationships.
                </p>
            </div>

            <GraphViz />
        </div>
    );
}
