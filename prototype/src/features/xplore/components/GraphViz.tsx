"use client";

import dynamic from "next/dynamic";
import { useEntities } from "@/features/entity/hooks/useEntities";
import { useRelationships } from "@/features/relationship/hooks/useRelationships";
import { useMemo } from "react";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
    ssr: false,
});

export default function GraphViz() {
    const { data: entities = [] } = useEntities();
    const { data: relationships = [] } = useRelationships();

    const graphData = useMemo(() => {
        const nodes = entities.map((e) => ({
            id: e.id,
            name: e.name.value,
            group: e.kind.major,
        }));

        const links = relationships.map((r) => ({
            source: "e1", // In a real app, this would be the source entity ID
            target: r.relatedEntityId,
            label: r.key,
        }));

        // For the prototype, we need to make sure links connect existing nodes.
        // Since relationships in our mock data don't have a 'sourceId' (context dependent),
        // we'll mock some links for visualization if nodes exist.

        // Improved mock link generation for visualization
        const vizLinks = relationships.map(r => ({
            source: "e1", // Hardcoded for prototype visualization as relationships are usually context-aware
            target: r.relatedEntityId
        })).filter(l => nodes.find(n => n.id === l.source) && nodes.find(n => n.id === l.target));

        return { nodes, links: vizLinks };
    }, [entities, relationships]);

    return (
        <div className="h-[600px] border rounded-lg overflow-hidden bg-white dark:bg-gray-800">
            <ForceGraph2D
                graphData={graphData}
                nodeLabel="name"
                nodeAutoColorBy="group"
                linkDirectionalArrowLength={3.5}
                linkDirectionalArrowRelPos={1}
            />
        </div>
    );
}
