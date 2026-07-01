<template>
  <main class="shell">
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Stage Outfit Match Agent</p>
        <h1>把一支舞，变成五套能上台的造型。</h1>
        <p class="hero-text">
          输入舞蹈题目或链接，选择你想要的舞台气质，智能体会给出全套衣服、鞋子、配饰、参考来源、搜索链接和 PDF 搭配报告。
        </p>
      </div>
      <div class="look-rack" aria-label="演出服灵感衣架">
        <div class="rack-line"></div>
        <div class="hanger h1"></div>
        <div class="hanger h2"></div>
        <div class="hanger h3"></div>
      </div>
    </section>

    <section class="workspace">
      <form class="control-panel" @submit.prevent="submit">
        <div class="panel-head">
          <Sparkles :size="20" />
          <span>造型输入</span>
        </div>

        <label class="field">
          <span>舞蹈题目或视频链接</span>
          <textarea
            v-model="form.dance_input"
            rows="5"
            placeholder="例如：NewJeans Super Shy / aespa Drama / 或粘贴 B站、YouTube、小红书链接"
          ></textarea>
        </label>

        <div class="field">
          <span>想要的风格</span>
          <div class="style-grid">
            <button
              v-for="style in styles"
              :key="style"
              type="button"
              :class="['chip', { active: form.style === style }]"
              @click="form.style = style"
            >
              {{ style }}
            </button>
          </div>
        </div>

        <div class="field">
          <span>预算</span>
          <div class="segmented">
            <button
              v-for="budget in budgets"
              :key="budget"
              type="button"
              :class="{ active: form.budget === budget }"
              @click="form.budget = budget"
            >
              {{ budget }}
            </button>
          </div>
        </div>

        <button class="primary" type="submit" :disabled="loading">
          <WandSparkles :size="18" />
          {{ loading ? '正在生成搭配' : '生成五套搭配' }}
        </button>

        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <aside class="log-panel">
        <div class="panel-head">
          <ListChecks :size="20" />
          <span>智能体运行日志</span>
        </div>
        <ol>
          <li v-for="log in logsToShow" :key="log">{{ log }}</li>
        </ol>
      </aside>
    </section>

    <section v-if="result" class="result">
      <div class="result-head">
        <div>
          <p class="eyebrow">Final Lookbook</p>
          <h2>演出服搭配推荐</h2>
        </div>
        <a v-if="result.report_id" class="download" :href="reportUrl(result.report_id)" target="_blank">
          <Download :size="18" />
          下载 PDF 报告
        </a>
      </div>

      <div class="analysis-grid">
        <article>
          <h3>舞蹈分析</h3>
          <p>{{ result.dance_analysis }}</p>
        </article>
        <article>
          <h3>参考来源</h3>
          <ul>
            <li v-for="source in result.reference_sources" :key="source">{{ source }}</li>
          </ul>
        </article>
      </div>

      <div class="keywords">
        <span v-for="keyword in result.style_keywords" :key="keyword">{{ keyword }}</span>
      </div>

      <div class="outfit-grid">
        <article v-for="(outfit, index) in result.outfits" :key="outfit.name" class="outfit-card">
          <div class="photo">
            <img :src="outfit.image_url" :alt="outfit.name" @error="useFallbackImage" />
            <span>¥{{ outfit.total_price }}</span>
          </div>
          <div class="card-body">
            <p class="rank">LOOK {{ index + 1 }}</p>
            <h3>{{ outfit.name }}</h3>
            <p>{{ outfit.concept }}</p>
            <p class="reference">{{ outfit.reference }}</p>
            <p class="shopping-note">图片为整套搭配参考图；下方按钮会打开对应平台的商品搜索结果。</p>

            <div class="items">
              <div v-for="item in outfit.items" :key="item.type + item.name" class="item-row">
                <img class="item-thumb" :src="item.image_url" :alt="item.name" @error="useFallbackImage" />
                <div>
                  <strong>{{ item.type }}</strong>
                  <span>{{ item.name }}</span>
                </div>
                <em>¥{{ item.price }}</em>
                <div class="links">
                  <a
                    v-for="(url, label) in item.links"
                    :key="label"
                    :href="url"
                    target="_blank"
                    rel="noreferrer"
                  >
                    {{ label }}
                  </a>
                </div>
              </div>
            </div>
          </div>
        </article>
      </div>

      <section class="notes">
        <h3>试穿建议</h3>
        <ol>
          <li v-for="note in result.styling_notes" :key="note">{{ note }}</li>
        </ol>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { Download, ListChecks, Sparkles, WandSparkles } from 'lucide-vue-next'
import { createOutfitPlan, reportUrl } from './api/agent'

const styles = ['甜美', '帅气', '性感', '休闲', '灵动', '韩系', '女团风', '学院风']
const budgets = ['低预算', '中预算', '高预算']

const form = reactive({
  dance_input: '我想跳 NewJeans《Super Shy》，想要适合学校舞台的女团风演出服。',
  style: '甜美',
  budget: '中预算'
})

const loading = ref(false)
const error = ref('')
const result = ref(null)
const liveLogs = ref([])

const logsToShow = computed(() => {
  if (result.value?.logs?.length) return result.value.logs
  if (liveLogs.value.length) return liveLogs.value
  return ['等待输入舞蹈题目或链接', '选择风格按钮', '点击生成搭配']
})

async function submit() {
  if (!form.dance_input.trim()) {
    error.value = '请先输入舞蹈题目或视频链接。'
    return
  }
  loading.value = true
  error.value = ''
  result.value = null
  liveLogs.value = ['正在读取舞蹈信息', '正在匹配舞台风格', '正在生成五套造型']
  try {
    result.value = await createOutfitPlan({ ...form })
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || '生成失败，请检查后端服务。'
  } finally {
    loading.value = false
  }
}

function useFallbackImage(event) {
  const svg = encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="900" height="1200" viewBox="0 0 900 1200">
      <rect width="900" height="1200" fill="#fbf7f1"/>
      <rect x="72" y="72" width="756" height="1056" fill="#f3c469" stroke="#181512" stroke-width="6"/>
      <circle cx="450" cy="318" r="128" fill="#d64b3a"/>
      <path d="M260 560h380l-62 360H322z" fill="#181512"/>
      <path d="M310 545c40-80 90-120 140-120s100 40 140 120" fill="none" stroke="#2f6f61" stroke-width="46" stroke-linecap="round"/>
      <text x="450" y="1030" text-anchor="middle" font-family="Arial" font-size="44" font-weight="700" fill="#181512">OUTFIT PREVIEW</text>
    </svg>
  `)
  event.target.src = `data:image/svg+xml;charset=utf-8,${svg}`
}
</script>
