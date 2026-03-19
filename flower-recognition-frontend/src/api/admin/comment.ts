import { get, del } from '@/net'

export const getCommentList = (params: any, success: (data: any) => void, failure?: (message: string, status: number, url: string) => void) => {
    const queryString = new URLSearchParams(params).toString();
    get(`/api/admin/comment/list?${queryString}`, success, failure);
}

export const deleteComment = (id: number, success: (data: any) => void, failure?: (message: string, status: number, url: string) => void) => {
    del(`/api/admin/comment/${id}`, success, failure);
}
