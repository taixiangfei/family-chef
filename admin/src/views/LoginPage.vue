<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-brand">
        <span class="login-mark"><ChefHat :size="26" /></span>
        <div><strong>家常主厨</strong><span>内容管理台</span></div>
      </div>
      <div class="login-heading">
        <h1>管理员登录</h1>
        <p>使用后台账号进入管理中心</p>
      </div>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item label="账号">
          <el-input v-model="form.username" size="large" autocomplete="username" placeholder="请输入管理员账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" size="large" type="password" show-password autocomplete="current-password" placeholder="请输入密码" @keyup.enter="submit" />
        </el-form-item>
        <el-alert v-if="error" :title="error" type="error" :closable="false" show-icon />
        <el-button class="login-submit" type="primary" size="large" :loading="loading" @click="submit">登录</el-button>
      </el-form>
      <p class="login-foot">后台账号由系统管理员创建并分配权限</p>
    </section>
    <aside class="login-context">
      <div class="context-copy">
        <p>FAMILY CHEF</p>
        <h2>让每一份教程都经得起厨房里的实际操作。</h2>
        <dl>
          <div><dt>内容</dt><dd>菜品、教程与版本审核</dd></div>
          <div><dt>用户</dt><dd>身份、状态与权限管理</dd></div>
          <div><dt>社区</dt><dd>评论、反馈与举报治理</dd></div>
        </dl>
      </div>
    </aside>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChefHat } from 'lucide-vue-next'
import { api, errorMessage } from '../lib/api'
import { setTokens, setUser } from '../lib/auth'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = reactive({ username: '', password: '' })

async function submit() {
  if (!form.username || !form.password) {
    error.value = '请输入账号和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/auth/login/password/', form)
    setTokens(data)
    const me = await api.get('/users/me/')
    if (!me.data.is_staff) throw new Error('该账号没有后台管理权限')
    setUser(me.data)
    router.replace('/')
  } catch (cause) {
    error.value = cause.message === '该账号没有后台管理权限' ? cause.message : errorMessage(cause, '账号或密码错误')
  } finally {
    loading.value = false
  }
}
</script>
