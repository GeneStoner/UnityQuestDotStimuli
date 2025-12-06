using UnityEngine;
using UnityEngine.InputSystem;
#if UNITY_ANDROID && !UNITY_EDITOR
using UnityEngine.XR;
#endif

public class XRInputAndExit : MonoBehaviour
{
    public InputActionProperty buttonAction; // Assign this in Inspector
    public float holdDuration = 2f;

    private float holdTimer = 0f;

    void Update()
    {
        if (buttonAction.action.ReadValue<float>() > 0.5f)
        {
            holdTimer += Time.deltaTime;
            if (holdTimer >= holdDuration)
            {
#if UNITY_EDITOR
                UnityEditor.EditorApplication.isPlaying = false;
#elif UNITY_ANDROID
                Application.Quit();
#endif
            }
        }
        else
        {
            holdTimer = 0f;
        }
    }
}