using UnityEngine;
using UnityEngine.InputSystem;

public class VRInputHandler : MonoBehaviour
{
    [Header("Input Settings")]
    public InputActionAsset inputActions;

    [Header("Stimulus Settings")]
    public GameObject stimulusObject;

    [Header("Stimulus Size Settings")]
    [Tooltip("Desired size of the stimulus in degrees of visual angle.")]
    public float desiredVisualAngleDegrees = 5f;

    [Tooltip("Distance from the viewer (camera) to the stimulus, in meters.")]
    public float stimulusDistance = 3f;

    // Input Actions
    private InputAction selectLeft;
    private InputAction navigateLeft;
    private InputAction cancelLeft;

    private InputAction selectRight;
    private InputAction navigateRight;
    private InputAction cancelRight;

    void OnEnable()
    {
        var actionMap = inputActions.FindActionMap("VRControls", throwIfNotFound: true);

        // Left Controller Actions
        selectLeft = actionMap.FindAction("Select", throwIfNotFound: true);
        navigateLeft = actionMap.FindAction("NavigateLeft", false);
        cancelLeft = actionMap.FindAction("Cancel", throwIfNotFound: true);

        selectLeft.Enable();
        if (navigateLeft != null) navigateLeft.Enable();
        cancelLeft.Enable();

        selectLeft.performed += OnSelectLeft;
        if (navigateLeft != null) navigateLeft.performed += OnNavigateLeft;
        cancelLeft.performed += OnCancelLeft;

        // Right Controller Actions
        selectRight = actionMap.FindAction("Select", throwIfNotFound: true);
        navigateRight = actionMap.FindAction("NavigateRight", false);
        cancelRight = actionMap.FindAction("Cancel", throwIfNotFound: true);

        selectRight.Enable();
        if (navigateRight != null) navigateRight.Enable();
        cancelRight.Enable();

        selectRight.performed += OnSelectRight;
        if (navigateRight != null) navigateRight.performed += OnNavigateRight;
        cancelRight.performed += OnCancelRight;

        // Scale the stimulus before showing
        ScaleStimulusToDegrees();

        ShowStimulus();
    }

    void OnDisable()
    {
        selectLeft.performed -= OnSelectLeft;
        if (navigateLeft != null) navigateLeft.performed -= OnNavigateLeft;
        cancelLeft.performed -= OnCancelLeft;

        selectRight.performed -= OnSelectRight;
        if (navigateRight != null) navigateRight.performed -= OnNavigateRight;
        cancelRight.performed -= OnCancelRight;

        selectLeft.Disable();
        if (navigateLeft != null) navigateLeft.Disable();
        cancelLeft.Disable();

        selectRight.Disable();
        if (navigateRight != null) navigateRight.Disable();
        cancelRight.Disable();
    }

    private void OnSelectLeft(InputAction.CallbackContext context)
    {
        Debug.Log("LEFT trigger pressed at " + Time.time);
        HideStimulus();
    }

    private void OnNavigateLeft(InputAction.CallbackContext context)
    {
        Vector2 nav = context.ReadValue<Vector2>();
        Debug.Log($"LEFT thumbstick moved: {nav}");
    }

    private void OnCancelLeft(InputAction.CallbackContext context)
    {
        Debug.Log("LEFT cancel pressed at " + Time.time);
    }

    private void OnSelectRight(InputAction.CallbackContext context)
    {
        Debug.Log("RIGHT trigger pressed at " + Time.time);
        HideStimulus();
    }

    private void OnNavigateRight(InputAction.CallbackContext context)
    {
        Vector2 nav = context.ReadValue<Vector2>();
        Debug.Log($"RIGHT thumbstick moved: {nav}");
    }

    private void OnCancelRight(InputAction.CallbackContext context)
    {
        Debug.Log("RIGHT cancel pressed at " + Time.time);
    }

    void ShowStimulus()
    {
        if (stimulusObject != null)
            stimulusObject.SetActive(true);
    }

    void HideStimulus()
    {
        if (stimulusObject != null)
            stimulusObject.SetActive(false);
    }

    /// <summary>
    /// Scales the stimulus so it subtends the desired visual angle at the desired distance.
    /// </summary>
    void ScaleStimulusToDegrees()
    {
        if (stimulusObject == null)
        {
            Debug.LogWarning("Stimulus object is null. Cannot scale.");
            return;
        }

        float angleRadians = desiredVisualAngleDegrees * Mathf.Deg2Rad;
        float sizeMeters = 2f * stimulusDistance * Mathf.Tan(angleRadians / 2f);

        stimulusObject.transform.localScale = new Vector3(sizeMeters, sizeMeters, 1f);

        // Optionally, position it at the correct distance
        Vector3 pos = stimulusObject.transform.localPosition;
        stimulusObject.transform.localPosition = new Vector3(pos.x, pos.y, stimulusDistance);

        Debug.Log($"Scaled stimulus to {desiredVisualAngleDegrees}° → size {sizeMeters:F3} meters at {stimulusDistance} meters distance.");
    }
}