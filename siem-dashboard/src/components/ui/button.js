import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cn } from "@/lib/utils"

const buttonVariants = {
  default: "btn btn-primary",
  destructive: "btn btn-danger",
  outline: "btn btn-secondary",
  secondary: "btn btn-secondary",
  ghost: "btn btn-secondary",
  link: "text-primary underline-offset-4 hover:underline",
}

const Button = React.forwardRef(({ className, variant = "default", size = "default", asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button"
  return (
    <Comp
      className={cn(buttonVariants[variant], className)}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button, buttonVariants }