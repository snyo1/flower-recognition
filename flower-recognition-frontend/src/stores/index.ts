import { defineStore } from "pinia";
import { reactive } from "vue";

interface User {
    id: number;
    username: string;
    email: string;
    role: string;
    registration_date: string;
}

export const useStore = defineStore('main', () => {
    const auth = reactive({
        user: null as User | null
    })
    
    return { auth }
})
