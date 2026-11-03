const fs = require('fs');
const path = require('path');

function finiteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function normalizeRect(rect, label) {
  const x = finiteNumber(rect && rect.x);
  const y = finiteNumber(rect && rect.y);
  const w = finiteNumber(rect && rect.w);
  const h = finiteNumber(rect && rect.h);
  if (x === null || y === null || w === null || h === null) {
    throw new Error(`Template chrome ${label} must include numeric x, y, w, and h`);
  }
  if (w < 0 || h < 0) {
    throw new Error(`Template chrome ${label} width and height must be non-negative`);
  }
  return { x, y, w, h };
}

function loadTemplateChromeProfile(profilePath) {
  if (!profilePath) {
    throw new Error('loadTemplateChromeProfile requires a profile path');
  }
  const absolutePath = path.resolve(profilePath);
  const profile = JSON.parse(fs.readFileSync(absolutePath, 'utf8'));
  profile.__profilePath = absolutePath;
  profile.__profileDir = path.dirname(absolutePath);
  return profile;
}

function getSlideSize(profile) {
  const size = profile.slideSize || {};
  const widthIn = finiteNumber(size.widthIn) || finiteNumber(size.w);
  const heightIn = finiteNumber(size.heightIn) || finiteNumber(size.h);
  if (!widthIn || !heightIn || widthIn <= 0 || heightIn <= 0) {
    throw new Error('Template chrome profile must include slideSize widthIn/heightIn');
  }
  return { widthIn, heightIn };
}

function resolveChromeAsset(profile) {
  const asset = (profile.chrome && profile.chrome.asset) || profile.chromeAsset;
  if (!asset) return null;
  if (path.isAbsolute(asset)) return asset;
  return path.resolve(profile.__profileDir || process.cwd(), asset);
}

function getChromePlacement(profile) {
  const size = getSlideSize(profile);
  const placement = (profile.chrome && profile.chrome.placement) || {
    x: 0,
    y: 0,
    w: size.widthIn,
    h: size.heightIn,
  };
  return normalizeRect(placement, 'chrome placement');
}

function addTemplateChrome(slide, profile, options = {}) {
  const assetPath = options.assetPath || resolveChromeAsset(profile);
  if (!assetPath) {
    throw new Error('Template chrome profile does not include a chrome asset');
  }
  const placement = options.placement || getChromePlacement(profile);
  slide.addImage({
    path: assetPath,
    x: placement.x,
    y: placement.y,
    w: placement.w,
    h: placement.h,
  });
  return placement;
}

function getSafeArea(profile) {
  if (!profile.safeArea) return null;
  return normalizeRect(profile.safeArea, 'safeArea');
}

function normalizeContentRegion(region, label) {
  const rect = region && region.region ? region.region : region;
  return {
    ...(region || {}),
    ...normalizeRect(rect, label),
  };
}

function getContentRegions(profile) {
  const rawRegions = profile.contentRegions;
  const regions = {};
  if (Array.isArray(rawRegions)) {
    rawRegions.forEach((region, index) => {
      const name = region && (region.id || region.name);
      if (name) {
        regions[name] = normalizeContentRegion(region, `contentRegions[${index}]`);
      }
    });
  } else if (rawRegions && typeof rawRegions === 'object') {
    Object.entries(rawRegions).forEach(([name, region]) => {
      regions[name] = normalizeContentRegion(region, `contentRegions.${name}`);
    });
  }

  const fallback = getSafeArea(profile) || {
    x: 0,
    y: 0,
    w: getSlideSize(profile).widthIn,
    h: getSlideSize(profile).heightIn,
    source: 'fallback-slide-size',
  };
  if (!regions.body) regions.body = { ...fallback, source: fallback.source || 'fallback-safeArea' };
  if (!regions.title) regions.title = regions.body;
  if (!regions.source) regions.source = regions.body;
  return regions;
}

function getContentRegion(profile, name = 'body') {
  const regions = getContentRegions(profile);
  return regions[name] || regions.body;
}

function getReservedZones(profile) {
  return (profile.reservedZones || []).map((zone, index) => ({
    ...zone,
    ...normalizeRect(zone, `reservedZones[${index}]`),
    id: zone.id || `reserved-zone-${index + 1}`,
  }));
}

function rectIntersectionArea(a, b) {
  const ax2 = a.x + a.w;
  const ay2 = a.y + a.h;
  const bx2 = b.x + b.w;
  const by2 = b.y + b.h;
  const xOverlap = Math.max(0, Math.min(ax2, bx2) - Math.max(a.x, b.x));
  const yOverlap = Math.max(0, Math.min(ay2, by2) - Math.max(a.y, b.y));
  return xOverlap * yOverlap;
}

function assertRectInSafeArea(rect, profile, label = 'element') {
  const safeArea = getSafeArea(profile);
  if (!safeArea) return true;
  const normalizedRect = normalizeRect(rect, label);
  const epsilon = 1e-6;
  const inside =
    normalizedRect.x + epsilon >= safeArea.x &&
    normalizedRect.y + epsilon >= safeArea.y &&
    normalizedRect.x + normalizedRect.w <= safeArea.x + safeArea.w + epsilon &&
    normalizedRect.y + normalizedRect.h <= safeArea.y + safeArea.h + epsilon;
  if (!inside) {
    throw new Error(
      `${label} is outside template chrome safeArea: ${JSON.stringify(normalizedRect)}`,
    );
  }
  return true;
}

function assertNoReservedZoneOverlap(rect, profile, label = 'element') {
  const normalizedRect = normalizeRect(rect, label);
  for (const zone of getReservedZones(profile)) {
    const area = rectIntersectionArea(normalizedRect, zone);
    if (area > 1e-6) {
      throw new Error(
        `${label} overlaps template reserved zone "${zone.id}": ${JSON.stringify(normalizedRect)}`,
      );
    }
  }
  return true;
}

function assertRectInContentRegion(rect, profile, regionName = 'body', label = 'element') {
  const region = getContentRegion(profile, regionName);
  const normalizedRect = normalizeRect(rect, label);
  const epsilon = 1e-6;
  const inside =
    normalizedRect.x + epsilon >= region.x &&
    normalizedRect.y + epsilon >= region.y &&
    normalizedRect.x + normalizedRect.w <= region.x + region.w + epsilon &&
    normalizedRect.y + normalizedRect.h <= region.y + region.h + epsilon;
  if (!inside) {
    throw new Error(
      `${label} is outside template chrome content region "${regionName}": ${JSON.stringify(
        normalizedRect,
      )}`,
    );
  }
  return true;
}

function insetRect(rect, inset = 0) {
  const normalizedRect = normalizeRect(rect, 'insetRect input');
  const insets =
    typeof inset === 'number'
      ? { left: inset, right: inset, top: inset, bottom: inset }
      : {
          left: finiteNumber(inset.left) || 0,
          right: finiteNumber(inset.right) || 0,
          top: finiteNumber(inset.top) || 0,
          bottom: finiteNumber(inset.bottom) || 0,
        };
  return {
    x: normalizedRect.x + insets.left,
    y: normalizedRect.y + insets.top,
    w: Math.max(0, normalizedRect.w - insets.left - insets.right),
    h: Math.max(0, normalizedRect.h - insets.top - insets.bottom),
  };
}

function fitGrid(region, options = {}) {
  const normalizedRegion = normalizeRect(region, 'fitGrid region');
  const cols = Math.max(1, Math.floor(options.cols || 1));
  const rows = Math.max(1, Math.floor(options.rows || 1));
  const gapX = finiteNumber(options.gapX) !== null ? options.gapX : finiteNumber(options.gap) || 0;
  const gapY = finiteNumber(options.gapY) !== null ? options.gapY : finiteNumber(options.gap) || 0;
  const cellW = (normalizedRegion.w - gapX * (cols - 1)) / cols;
  const cellH = (normalizedRegion.h - gapY * (rows - 1)) / rows;
  if (cellW < 0 || cellH < 0) {
    throw new Error(`fitGrid gaps exceed region size: ${JSON.stringify(normalizedRegion)}`);
  }
  const cells = [];
  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      cells.push({
        x: normalizedRegion.x + col * (cellW + gapX),
        y: normalizedRegion.y + row * (cellH + gapY),
        w: cellW,
        h: cellH,
        row,
        col,
      });
    }
  }
  return cells;
}

module.exports = {
  loadTemplateChromeProfile,
  getSlideSize,
  resolveChromeAsset,
  getChromePlacement,
  addTemplateChrome,
  getSafeArea,
  getContentRegions,
  getContentRegion,
  getReservedZones,
  rectIntersectionArea,
  assertRectInSafeArea,
  assertRectInContentRegion,
  assertNoReservedZoneOverlap,
  insetRect,
  fitGrid,
};
