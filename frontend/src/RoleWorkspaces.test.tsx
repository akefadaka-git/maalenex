import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AdminWorkspace, RoleWorkspace } from "./RoleWorkspaces";

describe("role workspaces", () => {
  it("shows passenger sample route controls without submitting a booking", () => {
    const onRidePreview = vi.fn();
    render(<RoleWorkspace role="passenger" language="en" onRidePreview={onRidePreview} />);
    expect(screen.getByRole("heading", { name: "Passenger journey workspace" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Open ride planner preview" }));
    expect(onRidePreview).toHaveBeenCalledOnce();
  });

  it("keeps driver availability as a local preview state", () => {
    render(<RoleWorkspace role="motorcycle_driver" language="en" onRidePreview={() => undefined} />);
    expect(screen.getByText("Unavailable (preview)")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Toggle preview availability" }));
    expect(screen.getByText("Available (preview)")).toBeTruthy();
  });

  it("renders synthetic fleet records", () => {
    render(<RoleWorkspace role="fleet_operator" language="en" onRidePreview={() => undefined} />);
    expect(screen.getByText("MN-DEMO-01")).toBeTruthy();
    expect(screen.getByText("Demo driver A")).toBeTruthy();
  });

  it("keeps administration read-only and explicitly restricted", () => {
    render(<AdminWorkspace language="en" />);
    expect(screen.getByText("Read-only demonstration")).toBeTruthy();
    expect(screen.getByText("DEMO-APPLICATION-01")).toBeTruthy();
    expect(screen.queryByRole("button")).toBeNull();
  });
});
