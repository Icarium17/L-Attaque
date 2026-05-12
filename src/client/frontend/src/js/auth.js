const API_URL ="/api/index.php";

const post = (formdata) =>
    fetch(API_URL, { method:"POST", body: formdata}).then(res => res.json());

export const authAPI = {
    async signin (nom ,motDepasse){
        const fd = new FormData();
        fd.append("action", "signin");
        fd.append("nom", nom);
        fd.append("motDepasse",motDepasse);
        return post(fd);
    },

    async signout (key){
        const fd = new FormData();
        fd.append("action", "signout");
        return post(fd);
    },
    
    async register (nom, motDepasse){
        const fd = new FormData();
        fd.append("action", "register");
        fd.append("nom", nom);
        fd.append("motDepasse",motDepasse);
        return post(fd);
    },
};
