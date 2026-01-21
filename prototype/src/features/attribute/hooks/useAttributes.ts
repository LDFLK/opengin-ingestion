import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { attributeService, Attribute } from "@/services/attributeService";

export const useAttributes = () => {
    return useQuery({
        queryKey: ["attributes"],
        queryFn: attributeService.getAttributes,
    });
};

export const useCreateAttribute = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: attributeService.createAttribute,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["attributes"] });
        },
    });
};

export const useAttributesByName = (name: string) => {
    return useQuery({
        queryKey: ["attributes", name],
        queryFn: () => attributeService.getAttributesByName(name),
        enabled: !!name,
    });
};

export const useAttribute = (id: string) => {
    return useQuery({
        queryKey: ["attribute", id],
        queryFn: () => attributeService.getAttributeById(id),
        enabled: !!id,
    });
};

export const useUpdateAttribute = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: attributeService.updateAttribute,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["attributes"] });
            queryClient.invalidateQueries({ queryKey: ["attributes", data.name] });
            queryClient.invalidateQueries({ queryKey: ["attribute", data.id] });
        },
    });
};
