import { forwardRef, type ButtonHTMLAttributes, type InputHTMLAttributes, type HTMLAttributes, type ReactNode, type AnchorHTMLAttributes, type DialogHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary" | "quiet" | "danger";
type ButtonSize = "small" | "medium" | "large";
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> { variant?: ButtonVariant; size?: ButtonSize; loading?: boolean; block?: boolean; }
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button({variant="primary",size="medium",loading=false,block=false,disabled,children,className="",...props},ref){
  return <button ref={ref} className={`mn-button mn-button--${variant} ${size==="medium"?"":`mn-button--${size}`} ${block?"mn-button--block":""} ${className}`.trim()} disabled={disabled||loading} aria-busy={loading||undefined} {...props}>{loading&&<span className="mn-spinner" aria-hidden="true"/>}{children}</button>;
});

export interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> { label: string; hint?: string; error?: string; }
export const TextField = forwardRef<HTMLInputElement,TextFieldProps>(function TextField({label,hint,error,id,className="",...props},ref){
  const fieldId=id||props.name;
  return <div className="mn-field-wrap"><label className="mn-field-label" htmlFor={fieldId}>{label}</label><input ref={ref} id={fieldId} className={`mn-field ${className}`.trim()} aria-invalid={!!error||undefined} aria-describedby={error?`${fieldId}-error`:hint?`${fieldId}-hint`:undefined} {...props}/>{error?<span className="mn-field-error" id={`${fieldId}-error`}>{error}</span>:hint?<span className="mn-field-hint" id={`${fieldId}-hint`}>{hint}</span>:null}</div>;
});

export function Card({children,className="",interactive=false,...props}:HTMLAttributes<HTMLDivElement>&{interactive?:boolean}){return <div className={`mn-card ${interactive?"mn-card--interactive":""} ${className}`.trim()} {...props}>{children}</div>;}
export function Badge({children,tone="neutral"}:{children:ReactNode;tone?:"neutral"|"success"|"warning"|"danger"|"info"}){return <span className={`mn-badge ${tone==="neutral"?"":`mn-badge--${tone}`}`}>{children}</span>;}

export interface NavItem { href:string; label:string; icon?:ReactNode; current?:boolean; }
export function BottomNavigation({items,label="Main navigation"}:{items:NavItem[];label?:string}){return <nav className="mn-nav" aria-label={label}>{items.map(item=><a key={item.href} className="mn-nav__link" href={item.href} aria-current={item.current?"page":undefined}>{item.icon&&<span aria-hidden="true">{item.icon}</span>}<span>{item.label}</span></a>)}</nav>;}

export const Dialog = forwardRef<HTMLDialogElement,DialogHTMLAttributes<HTMLDialogElement>&{title?:string;onRequestClose?:()=>void}>(function Dialog({title,children,className="",onRequestClose,...props},ref){
 return <dialog ref={ref} className={`mn-dialog ${className}`.trim()} aria-label={props["aria-label"]||title} {...props}><div className="mn-dialog__body"><button type="button" className="mn-dialog__close" aria-label="Close dialog" onClick={onRequestClose}>×</button>{title&&<h2>{title}</h2>}{children}</div></dialog>;
});
export function BottomSheet({children,className="",...props}:DialogHTMLAttributes<HTMLDialogElement>){return <dialog className={`mn-dialog mn-sheet ${className}`.trim()} {...props}><div className="mn-sheet__handle" aria-hidden="true"/><div className="mn-dialog__body">{children}</div></dialog>;}
export function Skeleton({variant="text",className="",...props}:HTMLAttributes<HTMLSpanElement>&{variant?:"text"|"title"}){return <span className={`mn-skeleton mn-skeleton--${variant} ${className}`.trim()} aria-hidden="true" {...props}/>;}
export function LoadingIndicator({label="Loading"}:{label?:string}){return <span role="status" aria-label={label} className="mn-spinner"/>;}
