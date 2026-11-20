/** MaaleNex ↔ IROKA typed integration contract. No live endpoint is implied. */
export type IrokaCapability = "language-assistance" | "journey-information" | "accessibility-assistance";
export type IrokaConnectionStatus = "not-connected" | "connected";
export interface IrokaCapabilityRequest {
  capability: IrokaCapability;
  locale: "am" | "en";
  requestId: string;
  input: string;
}
export interface IrokaCapabilityResponse {
  requestId: string;
  capability: IrokaCapability;
  output: string;
  safetyLabels: string[];
}
export interface IrokaProvider {
  readonly status: IrokaConnectionStatus;
  invoke(request: IrokaCapabilityRequest): Promise<IrokaCapabilityResponse>;
}
