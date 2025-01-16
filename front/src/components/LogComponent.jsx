import React, { useState, useEffect } from "react";
import "./logs.css";

const LogComponent = ({ gameId, logs, fetchLogs }) => {
  const [isLogOpen, setIsLogOpen] = useState(false);

  return (
     <div className="log-container">
       <button className="log-toggle" onClick={() => setIsLogOpen(!isLogOpen)}>
         📜
       </button>
 
       {isLogOpen && (
         <div className="log-window">
           <div className="log-messages">
             {logs.map((log) => (
               <div key={log.id} className="log-message">
                 {log.content || "No hay descripción disponible"}
               </div>
             ))}
           </div>
         </div>
       )}
     </div>
   );
 };
export default LogComponent;
