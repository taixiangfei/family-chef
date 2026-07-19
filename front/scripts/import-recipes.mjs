import { existsSync, readdirSync, readFileSync, writeFileSync, statSync } from 'node:fs'
import { basename, join, relative, resolve, sep } from 'node:path'

const projectRoot = resolve(process.cwd(), '..')
const howToCookRoot = process.env.HOWTOCOOK_PATH || localRoot('HowToCook', '/private/tmp/HowToCook')
const cookLikeHocRoot = process.env.COOKLIKEHOC_PATH || localRoot('CookLikeHOC', '/private/tmp/CookLikeHOC_sparse')
const outFile = join(process.cwd(), 'src/utils/cookbook.js')

const sourceProjects = [
  {
    name: 'Anduin2017/HowToCook',
    url: 'https://github.com/Anduin2017/HowToCook',
    note: '已导入菜谱目录与可解析的材料、步骤；项目许可证为 Unlicense。'
  },
  {
    name: 'Gar-b-age/CookLikeHOC',
    url: 'https://github.com/Gar-b-age/CookLikeHOC',
    note: '已从本地源码导入菜名、分类、材料、步骤和来源链接。'
  }
]

const skills = [
  {
    title: '厨房准备',
    subtitle: '先把工具、调味和清洁路线理顺',
    points: ['常用锅具：炒锅、汤锅、电饭煲、蒸架', '基础调味：盐、生抽、老抽、蚝油、醋、糖、淀粉', '分区备菜：生熟分开，刀板及时冲洗']
  },
  {
    title: '油温判断',
    subtitle: '新手最容易卡住的一步',
    points: ['三四成热适合滑蛋、煎豆腐', '五六成热适合大多数家常小炒', '七成热以上适合快速定型，不适合长时间翻炒']
  },
  {
    title: '去腥与焯水',
    subtitle: '鱼肉禽类更稳定的入口感',
    points: ['冷水下锅适合排骨、牛腩等血水多的食材', '热水短焯适合青菜和部分海鲜', '葱姜料酒负责去腥，别指望它们掩盖不新鲜']
  }
]

const howToCookCategories = {
  vegetable_dish: { key: 'vegetable', label: '素菜' },
  meat_dish: { key: 'meat', label: '荤菜' },
  staple: { key: 'staple', label: '主食' },
  'semi-finished': { key: 'semi_finished', label: '半成品' },
  dessert: { key: 'dessert', label: '甜品' },
  condiment: { key: 'condiment', label: '配料' },
  soup: { key: 'soup', label: '汤羹' },
  aquatic: { key: 'aquatic', label: '水产' },
  drink: { key: 'drink', label: '饮品' },
  breakfast: { key: 'breakfast', label: '早餐' }
}

const hocCategories = {
  主食: { key: 'staple', label: '主食' },
  凉拌: { key: 'cold_dish', label: '凉拌' },
  卤菜: { key: 'braised_cold', label: '卤菜' },
  早餐: { key: 'breakfast', label: '早餐' },
  汤: { key: 'soup', label: '汤羹' },
  炒菜: { key: 'hoc_stir_fry', label: '炒菜' },
  炖菜: { key: 'hoc_stew', label: '炖菜' },
  炸品: { key: 'hoc_fried', label: '炸品' },
  烤类: { key: 'hoc_roast', label: '烤类' },
  烫菜: { key: 'hoc_blanch', label: '烫菜' },
  煮锅: { key: 'hoc_hotpot', label: '煮锅' },
  砂锅菜: { key: 'hoc_casserole', label: '砂锅菜' },
  蒸菜: { key: 'hoc_steam', label: '蒸菜' },
  配料: { key: 'condiment', label: '配料' },
  饮品: { key: 'drink', label: '饮品' }
}

const imageByHint = [
  [/凉拌|黄瓜|莴笋|海带|冷/i, '/static/images/cucumber.png'],
  [/豆腐|麻婆|辣|红烧/i, '/static/images/mapo-tofu.png'],
  [/蒸|蛋羹|蒸蛋|水煮蛋/i, '/static/images/steamed-egg.png'],
  [/汤|砂锅|炖|煮锅|米线|馄饨/i, '/static/images/chicken-pot.png'],
  [/饭|面|主食|炒饭/i, '/static/images/fried-rice.png']
]

function localRoot(name, fallback) {
  const path = join(projectRoot, name)
  return existsSync(path) ? path : fallback
}

function walkMarkdown(root) {
  const files = []
  function walk(dir) {
    for (const item of readdirSync(dir)) {
      const path = join(dir, item)
      const stats = statSync(path)
      if (stats.isDirectory()) {
        if (item === '.git' || item === 'node_modules') continue
        walk(path)
      } else if (item.endsWith('.md')) {
        files.push(path)
      }
    }
  }
  walk(root)
  return files.sort((a, b) => a.localeCompare(b, 'zh-Hans-CN'))
}

function stripMd(value) {
  return value
    .replace(/!\[[^\]]*]\([^)]+\)/g, '')
    .replace(/\[[^\]]+]\([^)]+\)/g, (match) => match.match(/\[([^\]]+)]/)?.[1] || '')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    .replace(/\s+/g, ' ')
    .trim()
}

function titleFromMarkdown(markdown, fallback) {
  const title = markdown.match(/^#\s+(.+)$/m)?.[1] || fallback
  return stripMd(title).replace(/的做法$/, '').trim()
}

function firstParagraph(markdown, title) {
  const lines = markdown.split(/\r?\n/)
  const start = lines.findIndex((line) => line.startsWith('# '))
  const paragraphs = []
  let current = []
  for (const line of lines.slice(start + 1)) {
    if (line.startsWith('## ')) break
    if (!line.trim()) {
      if (current.length) {
        paragraphs.push(current.join(' '))
        current = []
      }
      continue
    }
    if (/^(预估|!|\[|>)/.test(line.trim())) continue
    current.push(line.trim())
  }
  if (current.length) paragraphs.push(current.join(' '))
  return stripMd(paragraphs[0] || `${title} 的家常做法，适合按步骤备菜和烹饪。`)
}

function normalizeHeading(value) {
  return stripMd(value)
    .replace(/[：:]/g, '')
    .replace(/\s+/g, '')
    .trim()
}

function sections(markdown) {
  const lines = markdown.split(/\r?\n/)
  const headings = []

  lines.forEach((line, index) => {
    const match = line.match(/^(#{2,6})\s+(.+?)\s*$/)
    if (match) {
      headings.push({
        level: match[1].length,
        title: normalizeHeading(match[2]),
        index
      })
    }
  })

  return headings.map((heading, index) => {
    const next = headings.slice(index + 1).find((item) => item.level <= heading.level)
    return {
      ...heading,
      body: lines.slice(heading.index + 1, next ? next.index : lines.length)
    }
  })
}

function section(markdown, headingNames) {
  const names = (Array.isArray(headingNames) ? headingNames : [headingNames]).map(normalizeHeading)
  return sections(markdown)
    .filter((item) => names.some((name) => item.title === name || item.title.includes(name)))
    .map((item) => item.body.join('\n'))
    .join('\n')
}

function isNoiseLine(line) {
  const trimmed = line.trim()
  return !trimmed || trimmed.startsWith('#') || trimmed.startsWith('![') || /^[-*]+\s*$/.test(trimmed)
}

function cleanupListText(value) {
  return stripMd(value)
    .replace(/^[（(]?\s*\d+\s*[）)]\s*/, '')
    .replace(/^\d+[.)、]\s*/, '')
    .replace(/^[：:，,；;。]\s*/, '')
    .trim()
}

function listItems(text) {
  const items = []
  let current = ''

  function pushCurrent() {
    const value = cleanupListText(current)
    if (value) items.push(value)
    current = ''
  }

  for (const rawLine of text.split(/\r?\n/)) {
    if (isNoiseLine(rawLine)) {
      pushCurrent()
      continue
    }

    const trimmed = rawLine.trim()
    const bullet = trimmed.match(/^[-*+]\s*(.+)$/)
    const numbered = trimmed.match(/^\d+[.)、]\s*(.+)$/)

    if (bullet || numbered) {
      pushCurrent()
      current = bullet?.[1] || numbered?.[1] || ''
      continue
    }

    if (current) {
      current += rawLine.match(/^[，,；;。]/) ? trimmed : ` ${trimmed}`
    }
  }

  pushCurrent()
  return items.filter(Boolean).slice(0, 120)
}

function plainLines(text) {
  return text
    .split(/\r?\n/)
    .map((line) => cleanupListText(line.trim()))
    .filter(Boolean)
    .filter((line) => !line.startsWith('#') && !line.startsWith('!['))
    .filter((line) => !line.startsWith('详细成分与配比'))
    .slice(0, 120)
}

function bullets(text) {
  const items = listItems(text)
  return items.length ? items : plainLines(text)
}

function numberedSteps(text) {
  const items = listItems(text)
  return items.length ? items : text
    .split(/\r?\n/)
    .map((line) => cleanupListText(line.trim()))
    .filter(Boolean)
    .slice(0, 120)
}

function introListItems(markdown) {
  const lines = markdown.split(/\r?\n/)
  const titleIndex = lines.findIndex((line) => /^#\s+/.test(line))
  const start = titleIndex >= 0 ? titleIndex + 1 : 0
  const end = lines.findIndex((line, index) => index > start && /^##\s+/.test(line))
  return bullets(lines.slice(start, end >= 0 ? end : lines.length).join('\n'))
}

function fallbackSteps(source, categoryLabel, ingredients) {
  if (source === 'CookLikeHOC' && categoryLabel === '饮品') {
    return ['按原文记录的规格或配料准备，成品饮品可开封后直接饮用。']
  }

  if (categoryLabel === '配料') {
    const known = ingredients.length ? `已知成分：${ingredients.join('、')}。` : '原文未公布完整配比。'
    return [known, '按少量多次原则试调，先做小份确认咸淡、甜度和辣度，再用于主菜。']
  }

  return ['当前菜谱未解析到标准步骤，请打开来源链接查看原文。']
}

function inferMethod(title, categoryLabel, markdown = '') {
  const text = `${title} ${categoryLabel} ${markdown.slice(0, 500)}`
  const methods = ['炒', '煎', '蒸', '煮', '炖', '烤', '炸', '凉拌', '卤', '焯', '空气炸锅', '砂锅']
  return methods.find((item) => text.includes(item)) || categoryLabel
}

function inferTime(title, categoryLabel, markdown = '') {
  const explicit = markdown.match(/(?:约|大约|需要|需|只需|大概)?\s*(\d{1,3})\s*分钟/)
  if (explicit) return Number(explicit[1])
  if (/汤|炖|卤|牛腩|排骨|猪蹄/.test(`${title}${categoryLabel}`)) return 45
  if (/凉拌|饮品|配料/.test(`${title}${categoryLabel}`)) return 10
  if (/主食|面|饭|早餐/.test(`${title}${categoryLabel}`)) return 25
  return 20
}

function inferDifficulty(markdown = '', categoryLabel = '') {
  const stars = markdown.match(/预估烹饪难度：\s*(★+)/)?.[1]?.length
  if (stars) {
    if (stars <= 1) return '入门'
    if (stars === 2) return '基础'
    if (stars === 3) return '中等'
    return '进阶'
  }
  if (/汤|炖|卤|烤/.test(categoryLabel)) return '中等'
  return '基础'
}

function inferImage(title, categoryLabel, method) {
  const text = `${title} ${categoryLabel} ${method}`
  return imageByHint.find(([pattern]) => pattern.test(text))?.[1] || '/static/images/tomato-egg.png'
}

function hash(input) {
  let value = 2166136261
  for (const char of input) {
    value ^= char.charCodeAt(0)
    value = Math.imul(value, 16777619)
  }
  return (value >>> 0).toString(36)
}

function githubPath(path) {
  return path.split(/[\\/]/).map(encodeURIComponent).join('/')
}

function howToCookRecipes() {
  const dishesRoot = join(howToCookRoot, 'dishes')
  return walkMarkdown(dishesRoot)
    .filter((file) => !file.includes(`${sep}template${sep}`))
    .map((file) => {
      const rel = relative(dishesRoot, file)
      const parts = rel.split(sep)
      const category = howToCookCategories[parts[0]]
      if (!category) return null
      const markdown = readFileSync(file, 'utf8')
      const title = titleFromMarkdown(markdown, basename(file, '.md'))
      const ingredientText = section(markdown, ['必备原料和工具', '原料', '材料', '配料', '已知成分', '品类'])
      const operationText = section(markdown, ['操作', '步骤', '做法'])
      const ingredients = bullets(ingredientText)
      const steps = numberedSteps(operationText)
      const method = inferMethod(title, category.label, markdown)

      return {
        id: `htc-${hash(rel)}`,
        title,
        category: category.key,
        categoryLabel: category.label,
        method,
        image: inferImage(title, category.label, method),
        time: inferTime(title, category.label, markdown),
        difficulty: inferDifficulty(markdown, category.label),
        servings: 1,
        source: 'HowToCook',
        sourcePath: `HowToCook/dishes/${rel.split(sep).join('/')}`,
        sourceUrl: `https://github.com/Anduin2017/HowToCook/blob/master/dishes/${githubPath(rel)}`,
        summary: firstParagraph(markdown, title),
        tags: [category.label, method, '开源菜谱'],
        ingredients: ingredients.length ? ingredients : ['参考原文准备主要食材和基础调味。'],
        steps: steps.length ? steps : fallbackSteps('HowToCook', category.label, ingredients),
        tips: ['用量可按人数等比例调整。', '第一次做建议先少放盐，出锅前再补味。']
      }
    })
    .filter(Boolean)
}

function cookLikeHocRecipes() {
  return Object.entries(hocCategories).flatMap(([dirName, category]) => {
    const dir = join(cookLikeHocRoot, dirName)
    try {
      return walkMarkdown(dir)
        .filter((file) => basename(file) !== 'README.md')
        .map((file) => {
          const rel = relative(cookLikeHocRoot, file)
          const markdown = readFileSync(file, 'utf8')
          const title = titleFromMarkdown(markdown, basename(file, '.md'))
          const ingredientText = section(markdown, ['原料', '材料', '配料', '已知成分', '品类'])
          const operationText = section(markdown, ['步骤', '操作', '做法'])
          const ingredients = bullets(ingredientText)
          const normalizedIngredients = ingredients.length ? ingredients : introListItems(markdown)
          const steps = numberedSteps(operationText)
          const method = inferMethod(title, category.label, markdown)
          return {
            id: `hoc-${hash(rel)}`,
            title,
            category: category.key,
            categoryLabel: category.label,
            method,
            image: inferImage(title, category.label, method),
            time: inferTime(title, category.label, markdown),
            difficulty: inferDifficulty(markdown, category.label),
            servings: 1,
            source: 'CookLikeHOC',
            sourcePath: `CookLikeHOC/${rel.split(sep).join('/')}`,
            sourceUrl: `https://github.com/Gar-b-age/CookLikeHOC/blob/main/${githubPath(rel)}`,
            summary: firstParagraph(markdown, title),
            tags: [category.label, method, '门店风格'],
            ingredients: normalizedIngredients.length ? normalizedIngredients : ['参考原文准备主要食材和基础调味。'],
            steps: steps.length ? steps : fallbackSteps('CookLikeHOC', category.label, normalizedIngredients),
            tips: ['CookLikeHOC 中部分用量是批量出餐口径，家庭制作建议按人数缩小比例。', '含复合料包或半成品时，可用相近食材替代并按口味微调。']
          }
        })
    } catch {
      return []
    }
  })
}

function buildCategoryTabs(recipes) {
  const seen = new Set()
  const tabs = [{ key: 'all', label: '全部' }]
  for (const recipe of recipes) {
    const uniqueKey = `${recipe.category}:${recipe.categoryLabel}`
    if (seen.has(uniqueKey)) continue
    seen.add(uniqueKey)
    tabs.push({ key: recipe.category, label: recipe.categoryLabel })
  }
  return tabs
}

const recipes = [...howToCookRecipes(), ...cookLikeHocRecipes()].sort((a, b) => {
  if (a.source !== b.source) return a.source.localeCompare(b.source)
  return a.title.localeCompare(b.title, 'zh-Hans-CN')
})
const categoryTabs = buildCategoryTabs(recipes)
const methodTags = [...new Set(recipes.map((recipe) => recipe.method).filter(Boolean))].slice(0, 24)

const content = `// This file is generated by scripts/import-recipes.mjs.
// Do not edit recipe entries manually; update the importer or source data instead.

export const sourceProjects = ${JSON.stringify(sourceProjects, null, 2)}

export const categoryTabs = ${JSON.stringify(categoryTabs, null, 2)}

export const methodTags = ${JSON.stringify(methodTags, null, 2)}

export const skills = ${JSON.stringify(skills, null, 2)}

export const recipes = ${JSON.stringify(recipes, null, 2)}

export function getRecipeById(id) {
  return recipes.find((recipe) => recipe.id === id)
}
`

writeFileSync(outFile, content)
console.log(`Generated ${recipes.length} recipes to ${outFile}`)
console.log(`HowToCook: ${recipes.filter((recipe) => recipe.source === 'HowToCook').length}`)
console.log(`CookLikeHOC: ${recipes.filter((recipe) => recipe.source === 'CookLikeHOC').length}`)
