using UnityEngine;
using UnityEngine.UI;

public class FixationUI_DotCross : MonoBehaviour
{
    public Image fixDot;
    public Image fixHArm;
    public Image fixVArm;

    public Color fixationColor = Color.yellow;

    [Range(2f, 200f)] public float dotPx = 30f;
    [Range(10f, 800f)] public float armLenPx = 120f;
    [Range(1f, 100f)] public float armThkPx = 6f;

    void LateUpdate()
    {
        CenterAndColor(fixDot);
        CenterAndColor(fixHArm);
        CenterAndColor(fixVArm);

        if (fixDot)  fixDot.rectTransform.sizeDelta  = new Vector2(dotPx, dotPx);
        if (fixHArm) fixHArm.rectTransform.sizeDelta = new Vector2(armLenPx, armThkPx);
        if (fixVArm) fixVArm.rectTransform.sizeDelta = new Vector2(armThkPx, armLenPx);
    }

    void CenterAndColor(Image img)
    {
        if (img == null) return;
        var rt = img.rectTransform;
        rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f);
        rt.anchoredPosition = Vector2.zero;
        img.color = fixationColor;
        img.gameObject.SetActive(true);
    }
}