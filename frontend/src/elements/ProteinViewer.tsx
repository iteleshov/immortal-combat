import React, { useEffect, useRef, useState } from "react";

export interface ProteinViewerProps {
  pdbUrl: string;
  autoRotate?: boolean;
  backgroundColor?: string;
}

export const ProteinViewer: React.FC<ProteinViewerProps> = ({
                                                              pdbUrl,
                                                              autoRotate = true,
                                                              backgroundColor = "white",
                                                            }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const container = containerRef.current;
    if (!container) return;

    const initStage = async () => {
      if (stageRef.current) {
        try {
          stageRef.current.dispose();
        } catch (e) {
          console.warn("Stage dispose failed:", e);
        }
        stageRef.current = null;
        container.innerHTML = "";
      }

      const { Stage } = await import("ngl");
      const stage = new Stage(container, { backgroundColor });
      stageRef.current = stage;

      setLoading(true);
      stage
        .loadFile(pdbUrl)
        .then((comp: any) => {
          comp.addRepresentation("cartoon", { colorScheme: "resname" });
          comp.autoView();
          if (autoRotate) stage.setSpin(true);
        })
        .catch((err: any) => console.error("NGL load error:", err))
        .finally(() => {
          if (isMounted) setLoading(false);
        });

      const handleResize = () => stage.handleResize();
      window.addEventListener("resize", handleResize);

      return () => {
        window.removeEventListener("resize", handleResize);
        stage.dispose();
      };
    };

    const cleanupPromise = initStage();

    return () => {
      isMounted = false;
      cleanupPromise?.then?.((cleanupFn) => cleanupFn?.());
    };
  }, [pdbUrl, autoRotate, backgroundColor]);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "500px",
        borderRadius: "12px",
        overflow: "hidden",
      }}
    >
      {loading && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundColor: "rgba(255,255,255,0.8)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 10,
          }}
        >
          <div
            style={{
              width: "48px",
              height: "48px",
              border: "4px solid #ccc",
              borderTop: "4px solid #007bff",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }}
          />
        </div>
      )}
      <div
        ref={containerRef}
        style={{
          width: "100%",
          height: "100%",
        }}
      />
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
