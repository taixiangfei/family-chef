import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'

import { categoryTabs, methodTags, recipes, sourceProjects } from '../src/utils/cookbook.js'

const output = resolve(process.cwd(), '../server/data/recipes.json')
const payload = {
  version: 1,
  categories: categoryTabs.filter((category) => category.key !== 'all'),
  tags: methodTags,
  sourceProjects,
  recipes
}

mkdirSync(dirname(output), { recursive: true })
writeFileSync(output, `${JSON.stringify(payload, null, 2)}\n`)
console.log(`Exported ${recipes.length} recipes to ${output}`)
