<template>
<el-form :inline="true" :model="formInline" size="small" >
  <el-form-item label="用户信息">
    <el-input class="input" v-model="formInline.username" placeholder="用户名"></el-input>
    <el-input class="input" v-model="formInline.email" placeholder="email"></el-input>
  </el-form-item>
 <el-form-item>
    <el-button type="primary" @click="onSubmitGet">get 查询所有</el-button>
    <el-button type="primary" @click="onSubmitPost">post 提交</el-button>
  </el-form-item>
 <el-input type="textarea" :rows="6" placeholder="此处返回结果" v-model="results" class="textarea"> </el-input>
</el-form>


</template>
<script>
  import axios from 'axios'
  export default {
    data() {
      return {
        formInline: {
          username: '',
          email: '',
        },
        results:''
      }
    },
    methods: {
      onSubmitGet() {
        console.log('submit! get');
          // axios.get('api/users/',).then(res => {//get()中的参数要与mock.js文件中的Mock.mock()配置的路由保持一致
          axios.get('http://127.0.0.1:8000/users.json',).then(res => {//get()中的参数要与mock.js文件中的Mock.mock()配置的路由保持一致
          this.results = JSON.stringify(res.data);
          console.log(res.data);//在console中看到数据
        }).catch(res => {
          console.log(res);//在console中看到数据
          alert('wrong');
        })


      },
      onSubmitPost() {
        console.log('submit! post');
          // axios.post('api/users/',this.formInline).then(res => {//get()中的参数要与mock.js文件中的Mock.mock()配置的路由保持一致
          axios.post('http://127.0.0.1:8000/users.json',this.formInline).then(res => {//get()中的参数要与mock.js文件中的Mock.mock()配置的路由保持一致
          console.log(res.data);//在console中看到数据
        }).catch(res => {
          console.log(res);//在console中看到数据
          alert('wrong');
          alert('wrong');
        })

      }
    }
  }
</script>

<style scoped>
.input {
  width: 200px
}
button {
  width: 100px
}
.textarea {
  width: 900px
}
</style>