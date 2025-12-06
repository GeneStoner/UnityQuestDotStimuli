using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;

public class VRDotsHandler : MonoBehaviour
{
    [Header("Input Settings")]
    public InputActionAsset inputActions;

    [Header("Stimulus Settings")]
    public GameObject[] stimulusObjects;

    // [Header("Video Player")]
    // public UnityEngine.Video.VideoPlayer videoPlayer;

    [Header("Directional Response Settings")]
    public GameObject[] directionalTargets;
    public GameObject selectorIcon;

    [Header("Fixation Point")]
    public GameObject fixationPoint;

    [Header("Raycast Settings")]
    public Transform rightHandTransform;
    public float raycastDistance = 10f;

    private InputAction selectLeft;
    private InputAction selectRight;
    private InputAction cancelLeft;
    private InputAction cancelRight;

    private bool experimentStarted = false;
    private List<GameObject> randomizedStimuli;
    private int currentStimulusIndex = 0;

    private enum ExperimentPhase
    {
        Idle,
        ShowingStimulus,
        AwaitingDirectionResponse
    }

    private ExperimentPhase currentPhase = ExperimentPhase.Idle;
    private int currentDirectionIndex = -1;

    void Awake()
    {
        Debug.Log("VRDotsHandler Awake");
    }

    void OnEnable()
    {
        // if (videoPlayer == null)
        //     Debug.LogWarning("Video Player is not assigned in Inspector.");

        if (fixationPoint != null)
            fixationPoint.SetActive(false);

        if (inputActions != null)
        {
            var actionMapLeft = inputActions.FindActionMap("XRI LeftHand", false);
            var actionMapRight = inputActions.FindActionMap("XRI RightHand", false);

            if (actionMapLeft != null)
            {
                selectLeft = actionMapLeft.FindAction("Select", false);
                cancelLeft = actionMapLeft.FindAction("Cancel", false);

                if (selectLeft != null)
                {
                    selectLeft.Enable();
                    selectLeft.performed += OnSelectLeft;
                }
                if (cancelLeft != null)
                {
                    cancelLeft.Enable();
                    cancelLeft.performed += OnCancelLeft;
                }
            }

            if (actionMapRight != null)
            {
                selectRight = actionMapRight.FindAction("Select", false);
                cancelRight = actionMapRight.FindAction("Cancel", false);

                if (selectRight != null)
                {
                    selectRight.Enable();
                    selectRight.performed += OnSelectRight;
                }
                if (cancelRight != null)
                {
                    cancelRight.Enable();
                    cancelRight.performed += OnCancelRight;
                }
            }
        }
        else
        {
            Debug.LogError("InputActionAsset is NULL! Assign it in the Inspector.");
        }

        HideAllStimuli();
        HideAllDirectionalTargets();
        if (selectorIcon != null)
            selectorIcon.SetActive(false);
    }

    void OnDisable()
    {
        if (selectLeft != null) selectLeft.performed -= OnSelectLeft;
        if (cancelLeft != null) cancelLeft.performed -= OnCancelLeft;

        if (selectRight != null) selectRight.performed -= OnSelectRight;
        if (cancelRight != null) cancelRight.performed -= OnCancelRight;

        if (selectLeft != null) selectLeft.Disable();
        if (cancelLeft != null) cancelLeft.Disable();
        if (selectRight != null) selectRight.Disable();
        if (cancelRight != null) cancelRight.Disable();
    }

    private void OnSelectLeft(InputAction.CallbackContext context)
{
    Debug.Log("✅ Left trigger pressed!");
    HandleSelect();
}

    private void OnSelectRight(InputAction.CallbackContext context)
{
    Debug.Log("✅ Right trigger pressed!");
    HandleSelect();
}

    private void OnCancelLeft(InputAction.CallbackContext context)
    {
        Debug.Log("LEFT cancel pressed");
    }

    private void OnCancelRight(InputAction.CallbackContext context)
    {
        Debug.Log("RIGHT cancel pressed");
    }

    void HandleSelect()
    {
        if (!experimentStarted)
        {
            StartExperiment();
        }
        else if (currentPhase == ExperimentPhase.ShowingStimulus)
        {
            StopStimulusAndPromptResponse();
        }
        else if (currentPhase == ExperimentPhase.AwaitingDirectionResponse)
        {
            ConfirmDirectionSelection();
        }
    }

    void StartExperiment()
    {
        Debug.Log("Experiment started.");
        experimentStarted = true;
        currentPhase = ExperimentPhase.ShowingStimulus;

        if (fixationPoint != null)
            fixationPoint.SetActive(true);

        randomizedStimuli = new List<GameObject>(stimulusObjects);
        Shuffle(randomizedStimuli);
        currentStimulusIndex = 0;

        if (randomizedStimuli.Count > 0)
        {
            ShowStimulus(randomizedStimuli[currentStimulusIndex]);
        }
        else
        {
            Debug.LogWarning("No stimuli found in randomizedStimuli!");
            experimentStarted = false;
        }
    }

    void StopStimulusAndPromptResponse()
    {
        Debug.Log("Stopping stimulus and prompting for directional response.");

        HideStimulus(randomizedStimuli[currentStimulusIndex]);
        currentPhase = ExperimentPhase.AwaitingDirectionResponse;

        ShowAllDirectionalTargets();
        if (selectorIcon != null)
            selectorIcon.SetActive(true);

        currentDirectionIndex = -1;
    }

    void ConfirmDirectionSelection()
    {
        if (currentDirectionIndex < 0)
        {
            Debug.Log("No direction selected yet.");
            return;
        }

        Debug.Log($"Selected Direction: {DirectionName(currentDirectionIndex)}");

        HideAllDirectionalTargets();
        if (selectorIcon != null)
            selectorIcon.SetActive(false);

        NextStimulus();
    }

    void NextStimulus()
    {
        currentStimulusIndex++;

        if (currentStimulusIndex < randomizedStimuli.Count)
        {
            currentPhase = ExperimentPhase.ShowingStimulus;
            ShowStimulus(randomizedStimuli[currentStimulusIndex]);
        }
        else
        {
            Debug.Log("All stimuli shown. Ending experiment.");
            experimentStarted = false;
            currentPhase = ExperimentPhase.Idle;

            if (fixationPoint != null)
                fixationPoint.SetActive(false);
        }
    }

    void ShowStimulus(GameObject stimulus)
    {
        if (stimulus == null)
        {
            Debug.LogWarning("Attempted to show null stimulus.");
            return;
        }

        Debug.Log("Showing stimulus: " + stimulus.name);
        stimulus.SetActive(true);

        // if (videoPlayer != null)
        //     videoPlayer.Play();
    }

    void HideStimulus(GameObject stimulus)
    {
        if (stimulus == null) return;

        // if (videoPlayer != null)
        //     videoPlayer.Stop();

        stimulus.SetActive(false);
    }

    void HideAllStimuli()
    {
        foreach (var s in stimulusObjects)
            if (s != null) s.SetActive(false);
    }

    void ShowAllDirectionalTargets()
    {
        if (directionalTargets == null) return;

        foreach (var t in directionalTargets)
            if (t != null) t.SetActive(true);
    }

    void HideAllDirectionalTargets()
    {
        if (directionalTargets == null) return;

        foreach (var t in directionalTargets)
            if (t != null) t.SetActive(false);
    }

    void Update()
    {
        if (currentPhase == ExperimentPhase.AwaitingDirectionResponse)
        {
            RaycastForDirection();
        }
    }

    void RaycastForDirection()
    {
        if (rightHandTransform == null) return;

        Ray ray = new Ray(rightHandTransform.position, rightHandTransform.forward);
        RaycastHit hit;

        if (Physics.Raycast(ray, out hit, raycastDistance))
        {
            for (int i = 0; i < directionalTargets.Length; i++)
            {
                if (hit.collider.gameObject == directionalTargets[i])
                {
                    if (i != currentDirectionIndex)
                    {
                        currentDirectionIndex = i;
                        HighlightDirection(i);
                    }
                }
            }
        }
    }

    void HighlightDirection(int index)
    {
        Debug.Log("Highlighting direction: " + DirectionName(index));

        if (selectorIcon != null)
            selectorIcon.transform.position = directionalTargets[index].transform.position;
    }

    string DirectionName(int index)
    {
        switch (index)
        {
            case 0: return "E";
            case 1: return "NE";
            case 2: return "N";
            case 3: return "NW";
            case 4: return "W";
            case 5: return "SW";
            case 6: return "S";
            case 7: return "SE";
            default: return "Unknown";
        }
    }

    void Shuffle(List<GameObject> list)
    {
        for (int i = list.Count - 1; i > 0; i--)
        {
            int j = Random.Range(0, i + 1);
            (list[i], list[j]) = (list[j], list[i]);
        }
    }
}