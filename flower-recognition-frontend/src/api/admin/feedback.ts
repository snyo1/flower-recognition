import { get } from '@/net'

export const getFeedbackList = (params: any, success: (data: any) => void, failure?: (message: string, status: number, url: string) => void) => {
    const queryString = new URLSearchParams(params).toString();
    get(`/api/admin/feedback/list?${queryString}`, success, failure);
}
