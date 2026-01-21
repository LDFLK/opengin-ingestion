import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { relationshipService, Relationship } from "@/services/relationshipService";

export const useRelationships = () => {
    return useQuery({
        queryKey: ["relationships"],
        queryFn: relationshipService.getRelationships,
    });
};

export const useCreateRelationship = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: relationshipService.createRelationship,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["relationships"] });
        },
    });
};

export const useRelationship = (id: string) => {
    return useQuery({
        queryKey: ["relationship", id],
        queryFn: () => relationshipService.getRelationshipById(id),
        enabled: !!id,
    });
};

export const useUpdateRelationship = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: relationshipService.updateRelationship,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["relationships"] });
            queryClient.invalidateQueries({ queryKey: ["relationship", data.id] });
        },
    });
};
