const TAB_PAGES = new Set([
  '/pages/index/index',
  '/pages/meal-plan/index',
  '/pages/profile/index'
])

export function isTabPage(url = '') {
  const path = url.split('?')[0]
  return TAB_PAGES.has(path)
}

export function openPage(url, replace = false) {
  if (isTabPage(url)) {
    uni.switchTab({ url: url.split('?')[0] })
    return
  }
  if (replace) {
    uni.redirectTo({ url })
    return
  }
  uni.navigateTo({ url })
}

export function openAfterAuth(url) {
  if (isTabPage(url)) {
    uni.switchTab({ url: url.split('?')[0] })
    return
  }
  uni.redirectTo({ url })
}
