var currentR = estimateCurrentR(area, current, era);
var gap = Math.max(0, t.targetMin - currentR);
var pctShort = currentR > 0 ? Math.round((gap / t.targetMin) * 100) : 100;
var headline, tier;
if (gap === 0) {
  tier = 0;
  headline = 'You\'re already at or above code target.';
} else if (gap >= 20) {
  tier = 1;
  headline = 'Significantly under code \u2014 ' + pctShort + '% short of target.';
} else if (gap >= 8) {
  tier = 2;
  headline = 'Moderately under code \u2014 ' + pctShort + '% short of target.';
} else {
  tier = 3;
  headline = 'Close to code \u2014 ' + pctShort + '% short of target.';
}
