const difficultyLabels = {
  easy: '入门',
  basic: '基础',
  medium: '进阶',
  hard: '困难'
}

const fallbackImage = '/static/images/tomato-egg.png'

function imageUrl(value) {
  return typeof value === 'string' && value.trim() ? value : fallbackImage
}

function tagNames(tags = []) {
  return tags.map((tag) => typeof tag === 'string' ? tag : tag.name).filter(Boolean)
}

export function mapCategories(categories = []) {
  return [
    { key: 'all', label: '全部' },
    ...categories.map((category) => ({ key: category.key, label: category.name }))
  ]
}

export function mapDishToRecipe(dish) {
  const tags = tagNames(dish.tags)
  const categoryLabel = dish.category_name || '家常菜'
  return {
    id: dish.recipe_id || dish.legacy_id || dish.id,
    dishId: dish.id,
    legacyId: dish.legacy_id,
    title: dish.name,
    category: dish.category,
    categoryLabel,
    method: tags[0] || categoryLabel,
    image: imageUrl(dish.cover_url),
    time: dish.cooking_minutes || 20,
    difficulty: difficultyLabels[dish.difficulty] || dish.difficulty || '基础',
    servings: dish.servings || 1,
    source: dish.source_project || '家常主厨',
    summary: dish.recipe_summary || `${dish.name} 的家常做法，适合按步骤备菜和烹饪。`,
    tags
  }
}

export function mapRecipeDetail(article) {
  const dish = article.dish || {}
  const version = article.current_version || {}
  const tags = tagNames(dish.tags)
  return {
    id: article.id,
    dishId: dish.id,
    legacyId: dish.legacy_id,
    title: article.title || dish.name,
    category: dish.category,
    categoryLabel: dish.category_name || '家常菜',
    method: tags[0] || dish.category_name || '家常菜',
    image: imageUrl(dish.cover_url),
    time: version.cooking_minutes || 20,
    difficulty: difficultyLabels[version.difficulty] || version.difficulty || '基础',
    servings: version.servings || 1,
    source: dish.source_project || '家常主厨',
    sourcePath: dish.source_path,
    sourceUrl: dish.source_url,
    likeCount: dish.like_count || 0,
    dislikeCount: dish.dislike_count || 0,
    commentCount: dish.comment_count || 0,
    summary: version.summary || '',
    tags,
    ingredients: (version.ingredients || []).map((item) => item.raw_text || item.name).filter(Boolean),
    steps: (version.steps || []).map((item) => item.description).filter(Boolean),
    tips: version.tips || []
  }
}

export function filterStaticRecipes(recipes, keyword, category) {
  const query = keyword.trim().toLowerCase()
  return recipes.filter((recipe) => {
    const categoryMatched = category === 'all' || recipe.category === category
    const searchText = [
      recipe.title,
      recipe.summary,
      recipe.method,
      recipe.difficulty,
      recipe.source,
      ...recipe.tags,
      ...recipe.ingredients
    ].join(' ').toLowerCase()
    return categoryMatched && (!query || searchText.includes(query))
  })
}
