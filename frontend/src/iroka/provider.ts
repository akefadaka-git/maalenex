import type { IrokaProvider } from "./contracts";

/** Fail-closed until endpoint, identity, protocol, and Owner approval are verified. */
const unavailableProvider: IrokaProvider = {
  status: "not-connected",
  async invoke() {
    throw new Error("IROKA is not connected. No intelligence request was sent.");
  }
};

export function getIrokaProvider(): IrokaProvider {
  return unavailableProvider;
}
