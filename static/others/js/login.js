var app = new Vue({
    el:'#app',
    data:{
        host:'',
        input_user:'',
        input_pwd:'',
    },
    methods:{
        login:function(){
            if(this.input_user==''&&this.input_user==''){
                this.$message.error('用户名密码不能为空');
            }
            else{
                axios.post(this.host+'/login',{
                    username:this.input_user,
                    password:this.input_pwd
                },{
                    responseType:'json',
                    changeOrigin: true,
                    withCredentials:true, 
                })
                .then(response=>{
                    if(response.data.code==0){
                        this.$message({
                            message: '登陆成功',
                            type: 'success'
                          });
                          localStorage.setItem('token',response.data.token)
                          window.location.href = '/'

                    }
                    else{
                        this.$message.error(response.data.errmsg);
                    }
                })
            }
        }
    }
})