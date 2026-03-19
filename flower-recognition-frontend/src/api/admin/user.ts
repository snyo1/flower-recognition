import { get, del } from '@/net'

export const getUserList = (params: any, success: (data: any) => void, failure?: (message: string, status: number, url: string) => void) => {
    const queryString = new URLSearchParams(params).toString();
    get(`/api/admin/user/list?${queryString}`, success, failure);
}

export const deleteUser = (id: number, success: (data: any) => void, failure?: (message: string, status: number, url: string) => void) => {
    del(`/api/admin/user/${id}`, success, failure);
}
