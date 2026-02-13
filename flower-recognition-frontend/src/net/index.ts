import axios from "axios";
import { ElMessage } from "element-plus";

const authItemName = "access_token"

const defaultError = (err: any) => {
    console.error(err);
    ElMessage.error('发生了一些错误，请联系管理员');
}

const defaultFailure = (message: string, status: number, url: string) => {
    console.warn(`请求地址: ${url}, 状态码: ${status}, 错误信息: ${message}`);
    ElMessage.warning(message);
}

function accessHeader() {
    const token = localStorage.getItem(authItemName);
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function internalPost(url: string, data: any, header: any, success: (data: any) => void, failure: (message: string, status: number, url: string) => void = defaultFailure, error: (err: any) => void = defaultError) {
    axios.post(url, data, { headers: header }).then(({ data, status }) => {
        if (status === 200) {
            if(data.access_token) {
                localStorage.setItem(authItemName, data.access_token);
            }
            success(data);
        } else {
            failure(data.detail || "请求失败", status, url);
        }
    }).catch(err => {
        if(err.response) {
            failure(err.response.data.detail || "请求失败", err.response.status, url);
        } else {
            error(err);
        }
    });
}

function internalGet(url: string, header: any, success: (data: any) => void, failure: (message: string, status: number, url: string) => void = defaultFailure, error: (err: any) => void = defaultError) {
    axios.get(url, { headers: header }).then(({ data, status }) => {
        if (status === 200) {
            success(data);
        } else {
            failure(data.detail || "请求失败", status, url);
        }
    }).catch(err => {
         if(err.response) {
            failure(err.response.data.detail || "请求失败", err.response.status, url);
        } else {
            error(err);
        }
    });
}

function get(url: string, success: (data: any) => void, failure: (message: string, status: number, url: string) => void = defaultFailure) {
    internalGet(url, accessHeader(), success, failure);
}

function post(url: string, data: any, success: (data: any) => void, failure: (message: string, status: number, url: string) => void = defaultFailure) {
    internalPost(url, data, accessHeader(), success, failure);
}

function internalDelete(url: string, header: any, success: (data: any) => void, failure: (message: string, status: number, url: string) => void = defaultFailure, error: (err: any) => void = defaultError) {
    axios.delete(url, { headers: header }).then(({ data, status }) => {
        if (status === 200) {
            success(data);
        } else {
            failure(data.detail || "请求失败", status, url);
        }
    }).catch(err => {
        if(err.response) {
            failure(err.response.data.detail || "请求失败", err.response.status, url);
        } else {
            error(err);
        }
    });
}

function del(url: string, success: (data: any) => void, failure: (message: string, status: number, url: string) => void = defaultFailure) {
    internalDelete(url, accessHeader(), success, failure);
}

export { get, post, del }
