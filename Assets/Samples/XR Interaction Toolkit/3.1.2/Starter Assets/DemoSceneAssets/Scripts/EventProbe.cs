using UnityEngine;

public class EventProbe : MonoBehaviour
{
    public void PingTrialEnd()  { Debug.Log("[EventProbe] OnTrialEnded fired"); }
    public void PingResponse()  { Debug.Log("[EventProbe] OnResponse fired"); }
    public void PingNull()      { Debug.Log("[EventProbe] OnNullTrial fired"); }
}