import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { entityService, Entity } from "@/services/entityService";

export const useEntities = () => {
    return useQuery({
        queryKey: ["entities"],
        queryFn: entityService.getEntities,
    });
};

export const useCreateEntity = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: entityService.createEntity,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["entities"] });
        },
    });
};

export const useEntity = (id: string) => {
    return useQuery({
        queryKey: ["entity", id],
        queryFn: () => entityService.getEntityById(id),
        enabled: !!id,
    });
};

export const useUpdateEntity = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: entityService.updateEntity,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["entities"] });
            queryClient.invalidateQueries({ queryKey: ["entity", data.id] });
        },
    });
};
