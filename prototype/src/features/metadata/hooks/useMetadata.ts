import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { metadataService, Metadata } from "@/services/metadataService";

export const useMetadata = () => {
    return useQuery({
        queryKey: ["metadata"],
        queryFn: metadataService.getMetadata,
    });
};

export const useCreateMetadata = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: metadataService.createMetadata,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["metadata"] });
        },
    });
};

export const useMetadataItem = (id: string) => {
    return useQuery({
        queryKey: ["metadata", id],
        queryFn: () => metadataService.getMetadataById(id),
        enabled: !!id,
    });
};

export const useUpdateMetadata = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: metadataService.updateMetadata,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["metadata"] });
            queryClient.invalidateQueries({ queryKey: ["metadata", data.id] });
        },
    });
};
