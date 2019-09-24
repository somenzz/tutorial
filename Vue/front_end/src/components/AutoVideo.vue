<template>

    <el-form
            label-position="right"
            label-width="120px"
            :model="formData"
            :rules="rules"
            ref="formData"
            size="small"
    >
        <el-form-item label="网站地址：" prop="url" >
            <el-autocomplete
                    class="url_select"
                    v-model="formData.url"
                    :fetch-suggestions="querySearch"
                    placeholder="请输入学习网址"
            ></el-autocomplete>
            <!--<el-select class="url_select" v-model="formData.url" filterable allow-create default-first-option-->
                       <!--placeholder="请选择要学习的网址">-->
                <!--<el-option v-for="item in urls" :key="item" :label="item" :value="item"></el-option>-->
            <!--</el-select>-->
        </el-form-item>
        <el-form-item label="登陆控制：">
            <el-checkbox v-model="formData.autoLogin" @change="handleCheckBox">自动登陆</el-checkbox>
        </el-form-item>
        <el-form-item label="用户信息：" style="margin-bottom:0px" required>
            <el-col :span="9">
                <el-form-item prop="username">
                    <el-input
                            class="input"
                            :disabled="!formData.autoLogin"
                            v-model="formData.username"
                            placeholder="用户名"
                    ></el-input>
                </el-form-item>
            </el-col>
            <el-col :span="9">
                <el-form-item prop="passwd">
                    <el-input
                            class="input"
                            :disabled="!formData.autoLogin"
                            v-model="formData.passwd"
                            placeholder="密码"
                            show-password
                    ></el-input>
                </el-form-item>
            </el-col>
        </el-form-item>
        <el-form-item label="从哪开始：">
            <el-radio-group v-model="formData.beginPlace" class="radio">
                <el-radio label="0" border>学习地图</el-radio>
                <el-radio label="1" border>我的课程</el-radio>
            </el-radio-group>
            <el-input
                    class="inputNum"
                    v-model="formData.learnMapNum"
                    prop="learnNum"
                    :disabled="formData.beginPlace == 1"
                    placeholder="学习地图列表中第几个，默认1"
            ></el-input>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm('formData')">开始学习</el-button>
            <el-button type="warning" @click="open">终止学习</el-button>
        </el-form-item>
        <el-input type="textarea" :rows="6" placeholder="此处返回结果" v-model="results" class="textarea"></el-input>
    </el-form>
</template>
<script>
    // var baseURL = window.location.protocol + "//" + window.location.host;
    var baseURL = window.location.protocol + "//" + "127.0.0.1:8888";
    import axios from "axios";

    export default {
        data() {
            return {
                urls: [],
                formData: {
                    url: "http://v4.21tb.com",
                    username: "",
                    passwd: "",
                    beginPlace: "0",
                    learnMapNum: "1",
                    autoLogin: true
                },
                results: "提示：\n" +
                    "1、当网站有验证码时，请不要勾选自动登陆，在弹出的浏览器窗口中手动登陆\n" +
                    "2、当自动登陆失败时，点击终止学习，然后取消勾选自动登陆，再手动登陆\n" +
                    "3、当网址不在列表中时，可以直接输入网址，并在下方选择输入的网址即可\n" +
                    "4、程序会记录上一次输入的内容，并在下一次自动填入",
                rules: {
                    url: [
                        {required: true, message: "请输入网址，参考列表中的格式", trigger: "change"}
                    ],
                    username: [
                        {required: true, message: "请输入用户名", trigger: "change"}
                    ],
                    passwd: [{required: true, message: "请输入密码", trigger: "change"}]
                }
            };
        },
        methods: {
            querySearch(queryString, cb) {
                var urls = this.urls;
                var results = queryString ? urls.filter(this.createFilter(queryString)) : urls;
                // 调用 callback 返回建议列表的数据
                cb(results);
            },
            createFilter(queryString) {
                return (url) => {
                    return (url.value.toLowerCase().indexOf(queryString.toLowerCase()) != -1);
                };
            },
            loadAll() {
                return [
                    {"value":"http://sxjtzx.21tb.com"},
                    {"value":"http://gecu.21tb.com"},
                    {"value":"http://e-learning.jsnx.net"},
                    {"value":"http://v4.21tb.com"},
                ];
            },
            open() {
                this.$confirm("此操作将停止自动学习任务, 是否继续?", "提示", {
                    confirmButtonText: "确定",
                    cancelButtonText: "取消",
                    type: "warning"
                })
                    .then(() => {
                        this.onSubmitKill();
                        this.$message({
                            type: "success",
                            message: "停止成功!"
                        });
                    })
                    .catch(() => {
                        this.$message({
                            type: "info",
                            message: "已取消"
                        });
                    });
            },
            handleCheckBox() {
                this.$refs["formData"].resetFields();
                this.results =
                    "当网站有验证码时，请不要勾选自动登陆，在弹出的浏览器窗口中手动登陆";
            },
            submitForm(formName) {
                if (this.formData.autoLogin === false) {
                    this.onSubmitBegin();
                } else {
                    this.$refs[formName].validate(valid => {
                        if (valid) {
                            this.onSubmitBegin();
                        } else {
                            console.log("error submit!!");
                            return false;
                        }
                    });
                }
            },
            onSubmitBegin() {
                axios
                    .post(baseURL + "/add_task/", this.formData)
                    .then(res => {
                        //get()中的参数要与mock.js文件中的Mock.mock()配置的路由保持一致
                        this.results = JSON.stringify(res.data);
                        console.log(res.data); //在console中看到数据
                        this.$message({message: "任务已提交", type: "success"});
                    })
                    .catch(res => {
                        this.$message({
                            message: "任务提交失败，请查看后台日志",
                            type: "error"
                        });
                        console.log(res.data); //在console中看到数据
                    });
            },
            get_param() {
                axios
                    .post(baseURL + "/get_param/")
                    .then(res => {
                        if (res.data.url != undefined) {
                            this.formData = res.data
                        };
                    })
                    .catch(res => {
                        this.$message({
                            message: "参数获取失败",
                            type: "error"
                        });
                    });
            },
            onSubmitKill() {
                console.log("submit! post");
                // axios.post('api/users/',this.formData).then(res => {//get()中的参数要与mock.js文件中的Mock.mock()配置的路由保持一致
                axios
                    .post(baseURL + "/kill_task/", this.formData)
                    .then(res => {
                        //get()中的参数要与mock.js文件中的Mock.mock()配置的路由保持一致
                        console.log(res.data); //在console中看到数据
                        this.results = JSON.stringify(res.data);
                    })
                    .catch(res => {
                        console.log(res); //在console中看到数据
                        alert("wrong");
                    });
            }
        },
        mounted() {
            this.urls = this.loadAll();
            this.get_param();
        },
    };

</script>

<style scoped>
    .center {
        margin: 0 auto;
    }

    form {
        margin: 0 auto;
        width: 900px;
        text-align: left;
        /*background: black;*/
        /*background: #E3EDCD;*/
        padding: 20px;
        /*color: #E3EDCD;*/
        border: 1px ridge black;
        /*border-right: 2px dashed #0F0;*/
    }

    .input {
        width: 260px;
        margin-right: 10px;
    }

    .url_select {
        width: 260px;
        margin-right: 10px;
    }

    .inputNum {
        width: 250px;
        margin-right: 100px;
        margin-left: 0px;
    }

    button {
        width: 100px;
    }

    .radio {
        width: 300px;
    }

    .textarea {
    }
</style>
