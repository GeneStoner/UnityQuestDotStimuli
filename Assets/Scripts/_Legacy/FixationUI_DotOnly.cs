using UnityEngine;
using UnityEngine.UI;

public class FixationUI_DotOnly : MonoBehaviour
{
    public Image fixDot;
    public Color fixationColor = Color.yellow;

    [Range(2f, 200f)]
    public float dotPx = 30f;

    void LateUpdate()
    {
        if (fixDot == null) return;

        // Center
        var rt = fixDot.rectTransform;
        rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f);
        rt.anchoredPosition = Vector2.zero;

        // Size + color
        rt.sizeDelta = new Vector2(dotPx, dotPx);
        fixDot.color = fixationColor;
    }
}